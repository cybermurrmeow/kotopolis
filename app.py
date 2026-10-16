import os
import re
from hashlib import sha256
from urllib.parse import urlsplit

from datetime import date, datetime
from functools import wraps
from html import escape

from dotenv import load_dotenv

from flask import (
    Response,
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    send_file,
    jsonify,
    session,
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect, CSRFError

from itsdangerous import URLSafeTimedSerializer, BadData

from sqlalchemy.exc import SQLAlchemyError

from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Cat, AdoptionRequest, FavoriteCat, utc_now
from media import media_paths, remove_managed_media, save_cat_media
from passwords import password_errors

from forms import (
    LoginForm,
    RegisterForm,
    CatForm,
    AdoptionForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ResendConfirmationForm,
)
from daily_story import register_daily_story

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.config["PUBLIC_BASE_URL"] = os.environ.get(
    "PUBLIC_BASE_URL", "http://127.0.0.1:5000"
).rstrip("/")
public_origin = urlsplit(app.config["PUBLIC_BASE_URL"])
if (
    public_origin.scheme not in {"http", "https"}
    or not public_origin.netloc
    or public_origin.username
    or public_origin.query
    or public_origin.fragment
    or public_origin.path
):
    raise RuntimeError(
        "PUBLIC_BASE_URL must be an HTTP(S) origin without credentials or a path"
    )

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    headers_enabled=True,
    enabled=os.environ.get("RATELIMIT_ENABLED", "true").lower() == "true",
)
cookie_secure = os.environ.get("COOKIE_SECURE", "true").lower() == "true"

app.config.update(
    SESSION_COOKIE_SECURE=cookie_secure,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    REMEMBER_COOKIE_SECURE=cookie_secure,
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SAMESITE="Lax",
)

csrf = CSRFProtect(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is not set. Copy .env.example to .env and generate a key."
    )

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///kotopolis.db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"hide_parameters": True}
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads", "cat_media")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.mail.ru")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "465"))
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "true").lower() == "true"
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


def cat_media_sources(cat):
    sources = media_paths(cat.photo_path, app.static_folder)
    if sources["external"]:
        return sources

    return {
        key: url_for("static", filename=value)
        for key, value in sources.items()
        if key != "external"
    }


app.jinja_env.globals["cat_media_sources"] = cat_media_sources
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "🌸 Пожалуйста, войдите в систему " "для доступа к этой странице"
)
login_manager.login_message_category = "warning"


class GuestUser:
    id = -1
    username = "Гость"
    email = ""
    role = "guest"
    email_confirmed = True
    must_change_password = False
    created_at = None
    last_login = None
    is_authenticated = True
    is_active = True
    is_anonymous = False

    @property
    def is_admin(self):
        return False

    def get_id(self):
        return "__kotopolis_guest__"


@login_manager.user_loader
def load_user(user_id):
    if user_id == "__kotopolis_guest__":
        return GuestUser()

    try:
        user = db.session.get(User, int(user_id))
        if (
            user
            and session.get("password_version")
            == sha256(user.password.encode()).hexdigest()
        ):
            return user
        return None

    except (ValueError, SQLAlchemyError) as error:
        app.logger.error("Ошибка загрузки пользователя (%s)", type(error).__name__)

        return None


@app.before_request
def restrict_guest_mode():
    if getattr(current_user, "role", None) != "guest":
        return None

    endpoint = request.endpoint

    if endpoint is None:
        return None

    if endpoint == "static":
        return None

    if endpoint == "logout" and request.method == "POST":
        return None

    allowed_get_endpoints = {
        "index",
        "dashboard",
        "cats",
        "cat_details",
        "guest_login",
    }

    if (
        request.method
        in (
            "GET",
            "HEAD",
            "OPTIONS",
        )
        and endpoint in allowed_get_endpoints
    ):
        return None

    flash(
        "В гостевом режиме доступен только просмотр. "
        "Чтобы сохранять избранное или отправлять заявки, войди в аккаунт.",
        "info",
    )

    return redirect(url_for("cats"))


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        if current_user.role != "admin":
            abort(403)

        return function(*args, **kwargs)

    return wrapper


def remember_password_version(user):
    session["password_version"] = sha256(user.password.encode()).hexdigest()


def favorite_return_url():
    referrer = urlsplit(request.referrer or "")
    if (
        referrer.netloc == request.host
        and referrer.path.startswith("/")
        and not referrer.path.startswith("//")
    ):
        return referrer.path + ("?" + referrer.query if referrer.query else "")
    return url_for("cats")


@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    db.session.rollback()
    app.logger.error("Database transaction failed (%s)", type(error).__name__)
    return render_template("500.html", error_code=503), 503


def mail_is_configured():
    return bool(app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"))


def _confirmation_resend_wait_seconds(
    user,
    cooldown_seconds=60,
):
    """
    Shared account-level cooldown for confirmation resends.

    Returns 0 when a new message may be sent, otherwise the
    remaining number of seconds.
    """

    sent_at = getattr(
        user,
        "email_code_sent_at",
        None,
    )

    if not sent_at:
        return 0

    elapsed = (utc_now() - sent_at).total_seconds()

    if elapsed >= cooldown_seconds:
        return 0

    return max(
        1,
        cooldown_seconds - int(elapsed),
    )


def send_confirmation_email_with_cooldown(
    user,
    cooldown_seconds=60,
):
    """
    Resend wrapper that does not regenerate a code or reset
    attempts while the cooldown is active.
    """

    wait = _confirmation_resend_wait_seconds(
        user,
        cooldown_seconds=cooldown_seconds,
    )

    if wait:
        return False, wait

    sent = send_confirmation_email(user)

    return sent, 0


def send_confirmation_email(user):
    import secrets
    from datetime import timedelta

    if not mail_is_configured():
        app.logger.warning("SMTP пока не настроен. Код подтверждения не отправлен.")
        return False

    code = f"{secrets.randbelow(1000000):06d}"
    safe_username = escape(user.username)
    user.email_code_hash = generate_password_hash(code)
    user.email_code_expires_at = utc_now() + timedelta(minutes=10)
    user.email_code_attempts = 0
    user.email_code_sent_at = utc_now()

    db.session.commit()

    message = Message(
        subject="Код подтверждения Котополиса",
        recipients=[user.email],
    )
    message.html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Котополис</title>
    </head>

    <body style="
        margin:0;
        padding:28px 16px;
        background:#f7f0f3;
        font-family:Arial,sans-serif;
        color:#342d31;
    ">
        <div style="
            max-width:520px;
            margin:auto;
            background:#ffffff;
            border:1px solid #eee2e8;
            border-radius:24px;
            padding:34px 28px;
            text-align:center;
        ">
            <div style="
                font-size:14px;
                font-weight:700;
                letter-spacing:.08em;
                text-transform:uppercase;
                color:#c05886;
                margin-bottom:12px;
            ">
                Котополис
            </div>

            <h1 style="
                margin:0;
                font-size:28px;
                line-height:1.15;
                color:#2f292d;
            ">
                Подтвердите почту
            </h1>

            <p style="
                color:#786c72;
                line-height:1.55;
                margin:14px 0 26px;
            ">
                Привет, <b>{safe_username}</b>!
                Введите этот код в Котополисе.
            </p>

            <div style="
                display:inline-block;
                padding:18px 26px;
                border-radius:18px;
                background:#f9e7ef;
                color:#9c3e68;
                font-size:36px;
                font-weight:800;
                letter-spacing:.22em;
                margin-bottom:22px;
            ">
                {code}
            </div>

            <p style="
                color:#8c8086;
                font-size:14px;
                margin:0;
            ">
                Код действует 10 минут.
            </p>

            <p style="
                color:#aaa0a5;
                font-size:12px;
                line-height:1.5;
                margin:26px 0 0;
            ">
                Если вы не создавали аккаунт,
                просто проигнорируйте это письмо.
            </p>
        </div>
    </body>
    </html>
    """

    try:
        mail.send(message)

        app.logger.info(
            "Код подтверждения отправлен для user_id=%s",
            user.id,
        )

        return True

    except Exception as error:
        app.logger.exception(
            "Ошибка отправки кода подтверждения: %s",
            error,
        )

        return False


def send_password_reset_email(user):
    if not mail_is_configured():
        return False

    token = serializer.dumps(
        {"user_id": user.id, "email": user.email, "password_sig": user.password[-16:]},
        salt="password-reset",
    )
    reset_url = app.config["PUBLIC_BASE_URL"] + url_for("reset_password", token=token)
    safe_username = escape(user.username)
    safe_reset_url = escape(reset_url, quote=True)
    message = Message(
        subject=("🔐 Восстановление пароля - " "Котополис"), recipients=[user.email]
    )
    message.html = f"""
    <div style="
        font-family:Arial,sans-serif;
        background:#FFF0F5;
        padding:25px;
    ">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            padding:28px;
            border-radius:18px;
        ">

            <h2 style="color:#FF1493;">
                Восстановление пароля 🔐
            </h2>

            <p>
                Ссылка запрошена для аккаунта:
                <b>{safe_username}</b>
            </p>

            <p>
                Она действует в течение одного часа.
            </p>

            <p style="text-align:center;margin:30px 0;">

                <a
                    href="{safe_reset_url}"
                    style="
                        background:#FF69B4;
                        color:white;
                        padding:13px 22px;
                        border-radius:12px;
                        text-decoration:none;
                        display:inline-block;
                    "
                >
                    Изменить пароль
                </a>

            </p>

            <p style="color:#777;font-size:14px;">
                Если вы не запрашивали смену пароля,
                просто проигнорируйте это письмо.
            </p>

        </div>

    </div>
    """

    try:
        mail.send(message)

        app.logger.info("Reset-письмо отправлено " "для user_id=%s", user.id)

        return True

    except Exception as error:
        app.logger.exception("Ошибка reset email: %s", error)

        return False


@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()

    app.logger.exception(
        "Unhandled server error",
        exc_info=error,
    )

    return render_template("500.html"), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return (
        render_template(
            "csrf_error.html",
            reason=getattr(error, "description", "Недействительный CSRF-токен."),
        ),
        400,
    )


@app.before_request
def enforce_confirmed_email_session():
    """
    Пользователь не должен сохранять доступ к закрытым
    страницам после того, как его email стал неподтверждённым.

    Например:
    пользователь меняет email -> email_confirmed=False ->
    текущая сессия немедленно перестаёт давать доступ.
    """

    if not current_user.is_authenticated:
        return None

    allowed_endpoints = {
        "static",
        "login",
        "logout",
        "register",
        "confirm_email",
        "resend_confirmation",
        "forgot_password",
        "reset_password",
    }

    if request.endpoint in allowed_endpoints:
        return None

    if current_user.email_confirmed is not True:
        logout_user()

        flash(
            "📧 Email аккаунта не подтверждён. "
            "Подтвердите адрес, чтобы продолжить работу.",
            "warning",
        )

        return redirect(url_for("resend_confirmation"))

    return None


@app.before_request
def enforce_temporary_password_change():
    if not current_user.is_authenticated:
        return None

    if not getattr(current_user, "must_change_password", False):
        return None

    if request.endpoint in {"static", "change_password", "logout"}:
        return None

    flash(
        "Сначала смените временный пароль, который выдал администратор.",
        "warning",
    )
    return redirect(url_for("change_password"))


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), " "microphone=(), " "geolocation=()"
    )
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    # CSP учитывает текущий Bootstrap / Font Awesome CDN,
    # inline CSS/JS существующего проекта,
    # data: favicon и внешние HTTPS-картинки.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "img-src "
        "'self' "
        "data: "
        "blob: "
        "https:; "
        "media-src "
        "'self' "
        "data: "
        "blob: "
        "https:; "
        "style-src "
        "'self' "
        "'unsafe-inline' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com; "
        "script-src "
        "'self' "
        "'unsafe-inline' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com; "
        "font-src "
        "'self' "
        "data: "
        "https://cdnjs.cloudflare.com "
        "https://cdn.jsdelivr.net; "
        "connect-src "
        "'self';"
    )

    if current_user.is_authenticated:
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route(
    "/register",
    methods=["GET", "POST"],
)
@limiter.limit("5 per hour", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data
        existing_username = User.query.filter(
            db.func.lower(User.username) == username.lower()
        ).first()

        if existing_username:
            form.username.errors.append("Этот логин уже занят")

        form.password.errors.extend(password_errors(password, username, email))

        if existing_username or form.password.errors:
            return render_template(
                "register.html",
                form=form,
            )

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(
                password,
                method="pbkdf2:sha256",
            ),
            role="user",
            email_confirmed=False,
        )

        try:
            db.session.add(user)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Не удалось создать аккаунт. Проверьте данные и попробуйте ещё раз.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            )

        sent = send_confirmation_email(user)
        ticket = serializer.dumps(
            {
                "user_id": user.id,
                "email": user.email,
            },
            salt="email-code-context",
        )

        if not sent:
            flash(
                "Аккаунт создан, но код пока не удалось отправить. "
                "Попробуйте отправить его ещё раз.",
                "warning",
            )

        return redirect(
            url_for(
                "verify_email_code",
                ticket=ticket,
            )
        )

    return render_template(
        "register.html",
        form=form,
    )


@app.route("/confirm_email/<token>")
def confirm_email(token):
    flash(
        "Подтверждение по ссылке больше не используется. " "Введите код из письма.",
        "info",
    )

    return redirect(url_for("login"))


@app.route(
    "/verify_email",
    methods=["GET", "POST"],
)
@limiter.limit("10 per 10 minutes", methods=["POST"])
def verify_email_code():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    ticket = request.args.get("ticket", "").strip()

    if not ticket:
        flash(
            "Сессия подтверждения не найдена.",
            "warning",
        )
        return redirect(url_for("login"))

    try:
        payload = serializer.loads(
            ticket,
            salt="email-code-context",
            max_age=86400,
        )
    except BadData:
        flash(
            "Сессия подтверждения устарела. Войдите снова.",
            "warning",
        )
        return redirect(url_for("login"))

    try:
        user_id = int(payload.get("user_id"))
    except (TypeError, ValueError, AttributeError):
        user_id = None

    user = db.session.get(User, user_id) if user_id else None

    if (
        not user
        or user.email.strip().lower() != str(payload.get("email", "")).strip().lower()
    ):
        flash(
            "Не удалось определить аккаунт.",
            "danger",
        )
        return redirect(url_for("login"))

    if user.email_confirmed:
        flash(
            "Почта уже подтверждена. Войдите в аккаунт.",
            "info",
        )

        return redirect(url_for("login"))

    error = None

    if request.method == "POST":
        code = request.form.get("code", "").strip()

        if len(code) != 6 or not code.isdigit():
            error = "Введите 6 цифр"

        elif not user.email_code_hash or not user.email_code_expires_at:
            error = "Код больше не действует. Отправьте новый."

        elif utc_now() > user.email_code_expires_at:
            error = "Код истёк. Отправьте новый."

        elif (user.email_code_attempts or 0) >= 5:
            error = "Слишком много попыток. Отправьте новый код."

        elif not check_password_hash(
            user.email_code_hash,
            code,
        ):
            user.email_code_attempts = (user.email_code_attempts or 0) + 1

            db.session.commit()

            left = max(
                0,
                5 - user.email_code_attempts,
            )
            error = (
                f"Неверный код. Осталось попыток: {left}"
                if left
                else "Слишком много попыток. Отправьте новый код."
            )

        else:
            user.email_confirmed = True
            user.email_confirmed_at = utc_now()
            user.email_code_hash = None
            user.email_code_expires_at = None
            user.email_code_attempts = 0
            user.email_code_sent_at = None
            user.last_login = utc_now()

            db.session.commit()

            login_user(user)
            remember_password_version(user)

            flash(
                "Почта подтверждена. Добро пожаловать в Котополис!",
                "success",
            )

            return redirect(url_for("dashboard"))

    masked_email = (
        user.email[:1] + "***@" + user.email.split("@", 1)[1]
        if "@" in user.email
        else user.email
    )

    return render_template(
        "verify_email.html",
        user=user,
        ticket=ticket,
        masked_email=masked_email,
        error=error,
    )


@app.route(
    "/resend_email_code",
    methods=["POST"],
)
@limiter.limit("3 per 5 minutes")
def resend_email_code():
    ticket = request.form.get(
        "ticket",
        "",
    ).strip()

    try:
        payload = serializer.loads(
            ticket,
            salt="email-code-context",
            max_age=86400,
        )
    except BadData:
        flash(
            "Сессия подтверждения устарела.",
            "warning",
        )
        return redirect(url_for("login"))

    try:
        user_id = int(payload.get("user_id"))
    except (TypeError, ValueError, AttributeError):
        user_id = None

    user = db.session.get(User, user_id) if user_id else None

    if (
        not user
        or user.email.strip().lower()
        != str(
            payload.get(
                "email",
                "",
            )
        )
        .strip()
        .lower()
    ):
        flash(
            "Сессия подтверждения устарела. Войдите снова.",
            "warning",
        )

        return redirect(url_for("login"))

    if user.email_confirmed:
        return redirect(url_for("login"))

    sent, wait = send_confirmation_email_with_cooldown(user)

    if wait:
        flash(
            f"Новый код можно отправить через {wait} сек.",
            "info",
        )

        return redirect(
            url_for(
                "verify_email_code",
                ticket=ticket,
            )
        )

    if sent:
        flash(
            "Новый код отправлен.",
            "success",
        )
    else:
        flash(
            "Не удалось отправить код. Попробуйте позже.",
            "danger",
        )

    return redirect(
        url_for(
            "verify_email_code",
            ticket=ticket,
        )
    )


@app.route("/resend_confirmation", methods=["GET", "POST"])
@limiter.limit("3 per 5 minutes", methods=["POST"])
def resend_confirmation():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = ResendConfirmationForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        user = User.query.filter(
            db.func.lower(User.username) == username.lower()
        ).first()

        if user and user.email.strip().lower() == email:
            if not user.email_confirmed:
                send_confirmation_email_with_cooldown(user)

        flash(
            "Если логин и email совпадают с аккаунтом, "
            "письмо подтверждения отправлено.",
            "info",
        )

        return redirect(url_for("login"))

    return render_template("resend_confirmation.html", form=form)


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        login_value = form.username_or_email.data.strip()
        password = form.password.data
        user = None
        user_by_username = User.query.filter(
            db.func.lower(User.username) == login_value.lower()
        ).first()

        if user_by_username:
            if check_password_hash(user_by_username.password, password):
                user = user_by_username

        elif "@" in login_value:
            email_users = User.query.filter(
                db.func.lower(User.email) == login_value.lower()
            ).all()
            password_matches = [
                candidate
                for candidate in email_users
                if check_password_hash(candidate.password, password)
            ]

            if len(password_matches) == 1:
                user = password_matches[0]

            elif len(password_matches) > 1:
                flash(
                    "На эту почту зарегистрировано несколько "
                    "аккаунтов с одинаковым паролем. "
                    "Введите логин нужного аккаунта.",
                    "warning",
                )

                return render_template("login.html", form=form)

        if not user:
            flash("Неверный логин, email или пароль", "danger")

            return render_template("login.html", form=form)

        if user.email_confirmed is not True:
            sent, wait = send_confirmation_email_with_cooldown(user)
            ticket = serializer.dumps(
                {
                    "user_id": user.id,
                    "email": user.email,
                },
                salt="email-code-context",
            )

            if wait:
                flash(
                    f"Новый код можно отправить через {wait} сек.",
                    "info",
                )

            elif sent:
                flash(
                    "Мы отправили новый код на вашу почту.",
                    "info",
                )

            else:
                flash(
                    "Почта ещё не подтверждена. " "Код пока не удалось отправить.",
                    "warning",
                )

            return redirect(
                url_for(
                    "verify_email_code",
                    ticket=ticket,
                )
            )

        login_user(user)
        remember_password_version(user)

        user.last_login = utc_now()

        db.session.commit()

        flash(f"Добро пожаловать, {user.username}! 🐱", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html", form=form)


@app.route("/guest_login", methods=["POST"])
def guest_login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_user(GuestUser(), remember=False)

    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    username = current_user.username

    logout_user()

    flash(f"До встречи, {username}! 🐾", "info")

    return redirect(url_for("login"))


@app.route("/forgot_password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        user = User.query.filter(
            db.func.lower(User.username) == username.lower()
        ).first()

        if user and user.email.strip().lower() == email:
            send_password_reset_email(user)

        flash(
            "Если логин и email совпадают с аккаунтом, "
            "ссылка для смены пароля отправлена.",
            "info",
        )

        return redirect(url_for("login"))

    return render_template("forgot_password.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    try:
        payload = serializer.loads(token, salt="password-reset", max_age=3600)

    except BadData:
        flash("Ссылка недействительна или устарела.", "danger")

        return redirect(url_for("forgot_password"))

    if not isinstance(payload, dict):
        flash(
            "Эта ссылка была создана по старой схеме. "
            "Запросите восстановление ещё раз.",
            "warning",
        )

        return redirect(url_for("forgot_password"))

    user_id = payload.get("user_id")
    token_email = str(payload.get("email", "")).strip().lower()
    password_sig = str(payload.get("password_sig", ""))

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        user_id = None

    user = db.session.get(User, user_id) if user_id else None

    if (
        not user
        or user.email.strip().lower() != token_email
        or user.password[-16:] != password_sig
    ):
        flash("Ссылка недействительна или уже была использована.", "danger")

        return redirect(url_for("forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        new_password = form.password.data

        form.password.errors.extend(
            password_errors(new_password, user.username, user.email)
        )

        if not form.password.errors:
            user.password = generate_password_hash(new_password, method="pbkdf2:sha256")
            user.must_change_password = False

            db.session.commit()

            flash(f"Пароль аккаунта {user.username} изменён 🩷", "success")

            return redirect(url_for("login"))

    return render_template(
        "reset_password.html", form=form, token=token, username=user.username
    )


@app.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    cats = Cat.query.order_by(Cat.id.desc()).all()
    recent_cats = Cat.query.order_by(Cat.id.desc()).limit(8).all()
    soon_ready = [cat for cat in cats if cat.status in ["На лечении", "В карантине"]]
    need_vacc = []

    for cat in cats:
        overdue_vaccine = cat.next_vacc_date is not None and cat.next_vacc_date < today

        if overdue_vaccine:
            cat.overdue_days = (today - cat.next_vacc_date).days

            need_vacc.append(cat)

    vaccination_known = [cat for cat in cats if cat.is_vaccinated is not None]
    sterilization_known = [cat for cat in cats if cat.is_sterilized is not None]
    vaccinated_count = len(
        [cat for cat in vaccination_known if cat.is_vaccinated is True]
    )
    sterilized_count = len(
        [cat for cat in sterilization_known if cat.is_sterilized is True]
    )
    need_vacc_count = len(need_vacc)
    vaccination_data_available = bool(vaccination_known)
    sterilization_data_available = bool(sterilization_known)
    stats = {
        "total": len(cats),
        "in_shelter": len([cat for cat in cats if cat.status == "В приюте"]),
        "adopted": len([cat for cat in cats if cat.status == "Усыновлён"]),
        "treatment": len([cat for cat in cats if cat.status == "На лечении"]),
        "quarantine": len([cat for cat in cats if cat.status == "В карантине"]),
        "vaccinated_count": vaccinated_count,
        "sterilized_count": sterilized_count,
        "need_vacc_count": need_vacc_count,
        "vaccination_data_available": vaccination_data_available,
        "sterilization_data_available": sterilization_data_available,
        "vaccination_rate": (
            vaccinated_count / len(vaccination_known) * 100
            if vaccination_known
            else None
        ),
        "sterilization_rate": (
            sterilized_count / len(sterilization_known) * 100
            if sterilization_known
            else None
        ),
        "need_vacc_rate": (need_vacc_count / len(cats) * 100 if cats else 0),
        "moods": {},
    }

    for cat in cats:
        mood = cat.mood if cat.mood else "Не указано"
        stats["moods"][mood] = stats["moods"].get(mood, 0) + 1

    return render_template(
        "dashboard.html",
        cats=cats,
        catalog_home_cats=sorted(
            (cat for cat in cats if cat.status == "В приюте"), key=lambda cat: cat.id
        ),
        stats=stats,
        recent_cats=recent_cats,
        need_vacc=need_vacc,
        soon_ready=soon_ready,
    )


@app.route("/cats")
@login_required
def cats():
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    mood = request.args.get("mood", "")
    gender = request.args.get("gender", "")
    personality = request.args.get("personality", "")
    activity_level = request.args.get("activity_level", "")
    vocal = request.args.get("vocal", "")
    sort = request.args.get("sort", "name")
    query = Cat.query

    if search:
        query = query.filter(
            Cat.name.ilike(f"%{search}%")
            | Cat.nickname.ilike(f"%{search}%")
            | Cat.breed.ilike(f"%{search}%")
            | Cat.color.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(Cat.status == status)

    if mood:
        query = query.filter(Cat.mood == mood)

    if gender:
        query = query.filter(Cat.gender == gender)

    if personality:
        query = query.filter(Cat.personality.ilike(f"%{personality}%"))

    if activity_level:
        query = query.filter(Cat.activity_level == activity_level)

    if vocal:
        query = query.filter(Cat.vocal == vocal)

    if sort == "name":
        query = query.order_by(Cat.name.asc())

    elif sort == "name_desc":
        query = query.order_by(Cat.name.desc())

    elif sort == "age":
        query = query.order_by(Cat.age.asc())

    elif sort == "age_desc":
        query = query.order_by(Cat.age.desc())

    elif sort == "newest":
        query = query.order_by(Cat.id.desc())

    elif sort == "oldest":
        query = query.order_by(Cat.id.asc())

    else:
        query = query.order_by(Cat.name.asc())

    cats_list = query.all()
    all_cats = Cat.query.all()
    moods = sorted({cat.mood for cat in all_cats if cat.mood})
    activity_levels = sorted(
        {cat.activity_level for cat in all_cats if cat.activity_level}
    )
    vocals = sorted({cat.vocal for cat in all_cats if cat.vocal})
    favorite_ids = []

    if current_user.is_authenticated:
        favorite_ids = [
            favorite.cat_id
            for favorite in FavoriteCat.query.filter_by(user_id=current_user.id).all()
        ]

    return render_template(
        "cats.html",
        cats=cats_list,
        favorite_ids=favorite_ids,
        moods=moods,
        activity_levels=activity_levels,
        vocals=vocals,
        search=search,
        status=status,
        mood=mood,
        gender=gender,
        personality=personality,
        activity_level=activity_level,
        vocal=vocal,
        sort=sort,
    )


@app.route("/cat/<int:cat_id>")
@login_required
def cat_details(cat_id):
    cat = db.get_or_404(Cat, cat_id)
    adoption_request = (
        AdoptionRequest.query.filter_by(cat_id=cat.id, user_id=current_user.id)
        .order_by(AdoptionRequest.id.desc())
        .first()
    )
    is_favorite = (
        FavoriteCat.query.filter_by(user_id=current_user.id, cat_id=cat.id).first()
        is not None
    )

    return render_template(
        "cat_details.html",
        cat=cat,
        adoption_request=adoption_request,
        is_favorite=is_favorite,
    )


def apply_cat_form(cat, form):
    old_status = cat.status
    new_status = form.status.data or "В приюте"
    allowed_statuses = {"В приюте", "Усыновлён", "На лечении", "В карантине"}

    if new_status not in allowed_statuses:
        raise ValueError("Некорректный статус котика")

    if (
        cat.id
        and new_status != "Усыновлён"
        and AdoptionRequest.query.filter_by(cat_id=cat.id, status="Одобрена").first()
    ):
        raise ValueError(
            "Сначала измените статус одобренной заявки, затем статус котика"
        )

    cat.name = form.name.data.strip()
    cat.nickname = form.nickname.data.strip() if form.nickname.data else None
    cat.age = form.age.data
    cat.breed = form.breed.data.strip() if form.breed.data else None
    cat.gender = form.gender.data or None
    cat.color = form.color.data.strip() if form.color.data else None
    cat.weight = form.weight.data
    cat.mood = form.mood.data or None
    cat.favorite_toy = (
        form.favorite_toy.data.strip() if form.favorite_toy.data else None
    )
    cat.arrival_date = form.arrival_date.data or cat.arrival_date or date.today()
    cat.status = new_status
    cat.health = form.health.data.strip() if form.health.data else None
    cat.description = form.description.data.strip() if form.description.data else None
    cat.last_vacc_date = form.last_vacc_date.data
    cat.next_vacc_date = form.next_vacc_date.data
    cat.is_vaccinated = bool(form.is_vaccinated.data)
    cat.is_sterilized = bool(form.is_sterilized.data)
    cat.personality = form.personality.data or None
    cat.activity_level = form.activity_level.data or None
    cat.kids_friendly = bool(form.kids_friendly.data)
    cat.cats_friendly = bool(form.cats_friendly.data)
    cat.dogs_friendly = bool(form.dogs_friendly.data)
    cat.favorite_place = (
        form.favorite_place.data.strip() if form.favorite_place.data else None
    )
    cat.food_preferences = (
        form.food_preferences.data.strip() if form.food_preferences.data else None
    )
    cat.vocal = form.vocal.data or None
    cat.story = form.story.data.strip() if form.story.data else None
    cat.adoption_recommendation = (
        form.adoption_recommendation.data.strip()
        if form.adoption_recommendation.data
        else None
    )

    if (
        cat.last_vacc_date
        and cat.next_vacc_date
        and cat.next_vacc_date < cat.last_vacc_date
    ):
        raise ValueError("Дата следующей прививки " "не может быть раньше предыдущей")

    if new_status == "Усыновлён":
        if old_status != "Усыновлён":
            cat.previous_status = old_status or "В приюте"

        cat.adoption_date = form.adoption_date.data or cat.adoption_date or date.today()

        if cat.arrival_date and cat.adoption_date < cat.arrival_date:
            raise ValueError(
                "Дата усыновления не может быть " "раньше даты поступления"
            )

        if cat.shelter_days_frozen is None:
            cat.shelter_days_frozen = cat.days_in_shelter

    else:
        if old_status == "Усыновлён":
            cat.previous_status = None

        cat.adoption_date = None
        cat.shelter_days_frozen = None

    # Save media only after all field/status/date checks.
    media = save_cat_media(form, app.config["UPLOAD_FOLDER"])

    if media:
        cat.photo_path = media

    cat.updated_at = utc_now()


@app.route("/add_cat", methods=["GET", "POST"])
@login_required
@admin_required
def add_cat():
    form = CatForm()

    if form.validate_on_submit():
        cat = Cat(
            name=form.name.data.strip(),
            arrival_date=(form.arrival_date.data or date.today()),
        )
        new_media_path = ""

        try:
            apply_cat_form(cat, form)

            new_media_path = cat.photo_path or ""

            db.session.add(cat)

            db.session.commit()

        except (
            ValueError,
            SQLAlchemyError,
        ) as exc:
            db.session.rollback()

            remove_managed_media(new_media_path, app.config["UPLOAD_FOLDER"])

            if isinstance(
                exc,
                ValueError,
            ):
                flash(str(exc), "danger")

            else:
                app.logger.error(
                    "Database error while adding cat (%s)", type(exc).__name__
                )

                flash(
                    "Не удалось сохранить котика. "
                    "Проверьте данные и попробуйте ещё раз.",
                    "danger",
                )

        else:
            flash("Котик добавлен 🐱", "success")

            return redirect(url_for("cat_details", cat_id=cat.id))

    return render_template("add_cat.html", form=form)


@app.route("/edit_cat/<int:cat_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_cat(cat_id):
    cat = db.session.execute(
        db.select(Cat).where(Cat.id == cat_id).with_for_update()
    ).scalar_one_or_none()
    if cat is None:
        abort(404)

    form = CatForm(obj=cat)

    if form.validate_on_submit():
        old_media_path = cat.photo_path or ""
        new_media_path = old_media_path

        try:
            apply_cat_form(cat, form)

            new_media_path = cat.photo_path or ""

            db.session.commit()

        except (
            ValueError,
            SQLAlchemyError,
        ) as exc:
            db.session.rollback()

            if new_media_path and new_media_path != old_media_path:
                remove_managed_media(new_media_path, app.config["UPLOAD_FOLDER"])

            if isinstance(
                exc,
                ValueError,
            ):
                flash(str(exc), "danger")

            else:
                app.logger.error(
                    "Database error while editing cat id=%s (%s)",
                    cat_id,
                    type(exc).__name__,
                )

                flash(
                    "Не удалось сохранить изменения. "
                    "Старые данные и изображение сохранены.",
                    "danger",
                )

        else:
            if old_media_path and old_media_path != new_media_path:
                try:
                    remove_managed_media(
                        old_media_path,
                        app.config["UPLOAD_FOLDER"],
                    )
                except OSError:
                    app.logger.exception("Failed to remove replaced cat media")

            flash("Данные котика сохранены", "success")

            return redirect(url_for("cat_details", cat_id=cat.id))

    return render_template("edit_cat.html", form=form, cat=cat)


@app.route("/delete_cat/<int:cat_id>", methods=["POST"])
@login_required
@admin_required
def delete_cat(cat_id):
    cat = db.get_or_404(Cat, cat_id)
    if cat.adoption_requests or cat.comments:
        flash(
            "Нельзя удалить котика с историческими заявками или комментариями. Измените статус карточки.",
            "warning",
        )
        return redirect(url_for("cat_details", cat_id=cat.id))

    media_path = cat.photo_path or ""

    db.session.delete(cat)

    db.session.commit()

    try:
        remove_managed_media(media_path, app.config["UPLOAD_FOLDER"])
    except OSError:
        app.logger.exception("Failed to remove cat media")

    flash("Котик удалён", "success")

    return redirect(url_for("cats"))


@app.route("/favorite/<int:cat_id>", methods=["POST"])
@login_required
def toggle_favorite(cat_id):
    cat = db.get_or_404(Cat, cat_id)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    favorite = FavoriteCat.query.filter_by(
        user_id=current_user.id, cat_id=cat_id
    ).first()

    if cat.status == "Усыновлён" and favorite is None:
        message = (
            "Этот котик уже дома и больше " "не доступен для добавления " "в избранное."
        )

        if is_ajax:
            return jsonify({"success": False, "error": message, "cat_id": cat_id}), 409

        flash(message, "info")

        return redirect(favorite_return_url())

    if favorite:
        db.session.delete(favorite)

        is_favorite = False

        if not is_ajax:
            flash("💔 Удалено из избранного", "info")

    else:
        favorite = FavoriteCat(user_id=current_user.id, cat_id=cat_id)

        db.session.add(favorite)

        is_favorite = True

        if not is_ajax:
            flash("💗 Добавлено в избранное", "success")

    db.session.commit()

    if is_ajax:
        return jsonify({"success": True, "cat_id": cat_id, "is_favorite": is_favorite})

    return redirect(favorite_return_url())


@app.route("/favorites")
@login_required
def favorites():
    favorite_rows = (
        FavoriteCat.query.filter_by(user_id=current_user.id)
        .order_by(FavoriteCat.created_at.desc())
        .all()
    )
    cats_list = [item.cat for item in favorite_rows]

    return render_template("favorites.html", cats=cats_list)


@app.route("/cat/<int:cat_id>/adopt", methods=["GET", "POST"])
@login_required
def create_adoption_request(cat_id):
    cat = db.session.execute(
        db.select(Cat).where(Cat.id == cat_id).with_for_update()
    ).scalar_one_or_none()
    if cat is None:
        abort(404)

    if cat.status != "В приюте":
        flash(
            "На этого котика сейчас нельзя " "подать заявку на усыновление.", "warning"
        )

        return redirect(url_for("cat_details", cat_id=cat.id))

    active_request = (
        AdoptionRequest.query.filter(
            AdoptionRequest.cat_id == cat.id,
            AdoptionRequest.user_id == current_user.id,
            AdoptionRequest.status.in_(["Новая", "На рассмотрении", "Одобрена"]),
        )
        .order_by(AdoptionRequest.id.desc())
        .first()
    )

    if active_request:
        flash(
            "У вас уже есть активная заявка "
            f"на {cat.name}. "
            "Её статус можно посмотреть в профиле.",
            "info",
        )

        return redirect(url_for("profile"))

    form = AdoptionForm()

    if request.method == "GET":
        form.email.data = current_user.email

    if form.validate_on_submit():
        db.session.refresh(cat)

        if cat.status != "В приюте":
            flash("Статус котика изменился. " "Заявку отправить уже нельзя.", "warning")

            return redirect(url_for("cat_details", cat_id=cat.id))

        duplicate = AdoptionRequest.query.filter(
            AdoptionRequest.cat_id == cat.id,
            AdoptionRequest.user_id == current_user.id,
            AdoptionRequest.status.in_(["Новая", "На рассмотрении", "Одобрена"]),
        ).first()

        if duplicate:
            flash("Такая активная заявка уже существует.", "warning")

            return redirect(url_for("profile"))

        adoption = AdoptionRequest(
            cat_id=cat.id,
            user_id=current_user.id,
            adopter_name=(form.adopter_name.data.strip()),
            age=form.age.data,
            phone=(form.phone.data.strip()),
            email=(form.email.data.strip().lower()),
            occupation=(form.occupation.data.strip()),
            housing=(form.housing.data.strip()),
            has_other_pets=(bool(form.has_other_pets.data)),
            experience=(form.experience.data.strip()),
            reason=(form.reason.data.strip()),
            comment=(form.comment.data.strip() if form.comment.data else None),
            request_date=date.today(),
            status="Новая",
        )

        db.session.add(adoption)

        db.session.commit()

        flash(
            f"Заявка на {cat.name} отправлена 🩷 "
            "Следить за её статусом можно в профиле.",
            "success",
        )

        return redirect(url_for("profile"))

    return render_template("adoption_form.html", form=form, cat=cat)


@app.route("/adoption_requests")
@login_required
@admin_required
def adoption_requests():
    status = request.args.get("status", "").strip()
    query = AdoptionRequest.query

    if status:
        query = query.filter(AdoptionRequest.status == status)

    requests_list = query.order_by(AdoptionRequest.request_date.desc()).all()

    return render_template("adoption_requests.html", requests=requests_list)


@app.route("/adoption_request/<int:request_id>/status", methods=["POST"])
@login_required
@admin_required
def update_adoption_request(request_id):
    adoption = db.get_or_404(AdoptionRequest, request_id)
    new_status = request.form.get("status", "").strip()
    allowed = {"Новая", "На рассмотрении", "Одобрена", "Отклонена", "Отменена"}

    if new_status not in allowed:
        abort(400)

    cat = db.session.execute(
        db.select(Cat).where(Cat.id == adoption.cat_id).with_for_update()
    ).scalar_one_or_none()
    db.session.refresh(adoption)
    old_status = adoption.status

    if not cat:
        abort(404)

    if old_status == "Отменена" and new_status != "Отменена":
        flash("Отменённую пользователем заявку нельзя возобновить.", "warning")
        return redirect(url_for("adoption_requests"))

    if (
        new_status in {"Новая", "На рассмотрении", "Одобрена"}
        and adoption.user_id is not None
    ):
        duplicate = AdoptionRequest.query.filter(
            AdoptionRequest.id != adoption.id,
            AdoptionRequest.cat_id == cat.id,
            AdoptionRequest.user_id == adoption.user_id,
            AdoptionRequest.status.in_(["Новая", "На рассмотрении", "Одобрена"]),
        ).first()
        if duplicate:
            flash("У пользователя уже есть активная заявка на этого котика.", "warning")
            return redirect(url_for("adoption_requests"))

    if new_status == "Одобрена":
        another_approved = AdoptionRequest.query.filter(
            AdoptionRequest.cat_id == cat.id,
            AdoptionRequest.id != adoption.id,
            AdoptionRequest.status == "Одобрена",
        ).first()

        if another_approved:
            flash("У этого котика уже есть " "одобренная заявка.", "warning")

            return redirect(url_for("adoption_requests"))

        if cat.status == "Усыновлён" and old_status != "Одобрена":
            flash("Котик уже отмечен как усыновлённый.", "warning")

            return redirect(url_for("adoption_requests"))

        if old_status != "Одобрена":
            cat.previous_status = cat.status

        cat.status = "Усыновлён"
        cat.adoption_date = date.today()
        cat.shelter_days_frozen = cat.days_in_shelter
        adoption.status = "Одобрена"
        other_requests = AdoptionRequest.query.filter(
            AdoptionRequest.cat_id == cat.id,
            AdoptionRequest.id != adoption.id,
            AdoptionRequest.status.in_(["Новая", "На рассмотрении"]),
        ).all()

        for item in other_requests:
            item.status = "Отклонена"

        db.session.commit()

        flash(f"Заявка одобрена. " f"{cat.name} отмечен как усыновлённый 🏡", "success")

        return redirect(url_for("adoption_requests"))

    if old_status == "Одобрена" and new_status != "Одобрена":
        cat.status = cat.previous_status or "В приюте"
        cat.adoption_date = None
        cat.shelter_days_frozen = None
        cat.previous_status = None

    adoption.status = new_status

    db.session.commit()

    flash("Статус заявки обновлён", "success")

    return redirect(url_for("adoption_requests"))


@app.route("/adoption_request/<int:request_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_adoption_request(request_id):
    db.get_or_404(AdoptionRequest, request_id)
    flash(
        "Заявки сохраняются в истории. Для закрытия измените статус заявки.", "warning"
    )
    return redirect(url_for("adoption_requests"))


@app.route("/profile")
@login_required
def profile():
    my_requests = (
        AdoptionRequest.query.filter_by(user_id=current_user.id)
        .order_by(AdoptionRequest.request_date.desc())
        .all()
    )
    favorite_count = FavoriteCat.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "profile.html",
        user=current_user,
        requests=my_requests,
        favorite_count=favorite_count,
    )


@app.route("/users")
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()

    return render_template("users.html", users=users_list)


@app.route("/users/create", methods=["POST"])
@login_required
@admin_required
def create_user():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user").strip()
    errors = []

    if not (3 <= len(username) <= 30):
        errors.append("Логин должен быть от 3 до 30 символов.")

    if not re.fullmatch(r"[a-zA-Z0-9_а-яА-ЯёЁ-]+", username):
        errors.append(
            "Логин может содержать только буквы, "
            "цифры, дефис и нижнее подчёркивание."
        )

    duplicate_username = User.query.filter(
        db.func.lower(User.username) == username.lower()
    ).first()

    if duplicate_username:
        errors.append("Пользователь с таким логином уже существует.")

    if (
        not email
        or len(email) > 120
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        errors.append("Введите корректный email.")

    errors.extend(password_errors(password, username, email))

    allowed_roles = {"user", "admin"}

    if role not in allowed_roles:
        errors.append("Некорректная роль пользователя.")

    if errors:
        for error in errors:
            flash(error, "danger")

        return redirect(url_for("users"))

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password, method="pbkdf2:sha256"),
        role=role,
        email_confirmed=False,
        email_confirmed_at=None,
        must_change_password=True,
    )

    db.session.add(user)

    db.session.commit()

    sent = send_confirmation_email(user)
    if sent:
        flash(
            "Пользователь создан. На его email отправлен код подтверждения.", "success"
        )
    else:
        flash(
            "Пользователь создан, но письмо "
            "подтверждения отправить не удалось. "
            "Его можно запросить повторно.",
            "warning",
        )

    return redirect(url_for("users"))


@app.route("/user/<int:user_id>/role", methods=["POST"])
@login_required
@admin_required
def update_user_role(user_id):
    user = db.get_or_404(User, user_id)
    role = request.form.get("role", "").strip()
    admins = (
        User.query.filter_by(role="admin").order_by(User.id).with_for_update().all()
    )
    allowed_roles = {"user", "admin"}

    if role not in allowed_roles:
        abort(400)

    if user.id == current_user.id and role != "admin":
        flash("Нельзя снять роль администратора " "с самого себя.", "warning")

        return redirect(url_for("users"))

    if user.role == "admin" and role != "admin":
        admin_count = len(admins)

        if admin_count <= 1:
            flash("Нельзя снять роль у последнего " "администратора.", "warning")

            return redirect(url_for("users"))

    if user.role == role:
        flash("У пользователя уже установлена " "эта роль.", "info")

        return redirect(url_for("users"))

    user.role = role

    db.session.commit()

    flash("Роль пользователя изменена.", "success")

    return redirect(url_for("users"))


@app.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    admins = (
        User.query.filter_by(role="admin").order_by(User.id).with_for_update().all()
    )
    user = db.get_or_404(User, user_id)
    if user.adoption_requests or user.comments:
        flash(
            "Нельзя удалить аккаунт с историческими заявками или комментариями.",
            "warning",
        )
        return redirect(url_for("users"))

    if user.id == current_user.id:
        flash(
            "Нельзя удалить свой собственный аккаунт " "из панели администратора.",
            "warning",
        )

        return redirect(url_for("users"))

    if user.role == "admin":
        admin_count = len(admins)

        if admin_count <= 1:
            flash("Нельзя удалить последнего администратора.", "warning")

            return redirect(url_for("users"))

    username = user.username

    db.session.delete(user)

    db.session.commit()

    flash(f"Пользователь {username} удалён.", "success")

    return redirect(url_for("users"))


@app.route("/exports")
@login_required
@admin_required
def exports_center():
    return render_template("exports.html")


@app.route("/export_cats_csv")
@login_required
@admin_required
def export_cats_csv():
    from utils import export_to_csv

    data = export_to_csv(Cat.query.order_by(Cat.id.asc()).all())
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=kotopolis_cats.csv"},
    )


@app.route("/export_cats_excel")
@login_required
@admin_required
def export_cats_excel():
    from utils import export_to_excel

    data = export_to_excel(Cat.query.order_by(Cat.id.asc()).all())
    return send_file(
        data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="kotopolis_cats.xlsx",
    )


@app.route("/export_cats_pdf")
@login_required
@admin_required
def export_cats_pdf():
    from utils import calculate_stats, generate_pdf_report

    cats_list = Cat.query.order_by(Cat.id.asc()).all()
    data = generate_pdf_report(cats_list, calculate_stats(cats_list))
    return send_file(
        data,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="kotopolis_cats.pdf",
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    errors = {}
    username = current_user.username
    email = current_user.email

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not 3 <= len(username) <= 30:
            errors["username"] = "Логин должен быть от 3 до 30 символов"
        elif not re.fullmatch(r"[a-zA-Z0-9_а-яА-ЯёЁ-]+", username):
            errors["username"] = "Используйте только буквы, цифры, _ и -"
        elif User.query.filter(
            db.func.lower(User.username) == username.lower(),
            User.id != current_user.id,
        ).first():
            errors["username"] = "Этот логин уже занят"

        if not email:
            errors["email"] = "Введите email"
        elif len(email) > 120:
            errors["email"] = "Email не должен превышать 120 символов"
        elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            errors["email"] = "Введите корректный email"

        if errors:
            return render_template(
                "edit_profile.html",
                errors=errors,
                username=username,
                email=email,
            )

        email_changed = current_user.email.strip().lower() != email
        current_user.username = username
        current_user.email = email

        if email_changed:
            current_user.email_confirmed = False
            current_user.email_confirmed_at = None
            current_user.email_code_hash = None
            current_user.email_code_expires_at = None
            current_user.email_code_attempts = 0
            current_user.email_code_sent_at = None

        try:
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            app.logger.error(
                "Failed to update profile for user_id=%s (%s)",
                current_user.id,
                type(error).__name__,
            )
            flash("Не удалось сохранить профиль. Попробуйте ещё раз.", "danger")
            return render_template(
                "edit_profile.html",
                errors={},
                username=username,
                email=email,
            )

        if email_changed:
            sent = send_confirmation_email(current_user)
            ticket = serializer.dumps(
                {"user_id": current_user.id, "email": current_user.email},
                salt="email-code-context",
            )
            logout_user()
            flash(
                "Профиль сохранён. "
                + (
                    "На новую почту отправлен код подтверждения."
                    if sent
                    else "Код подтверждения пока не удалось отправить."
                ),
                "success" if sent else "warning",
            )
            return redirect(url_for("verify_email_code", ticket=ticket))

        flash("Профиль сохранён", "success")
        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        errors={},
        username=username,
        email=email,
    )


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    errors = {}

    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not old_password:
            errors["old_password"] = "Введите текущий пароль"

        elif not check_password_hash(current_user.password, old_password):
            errors["old_password"] = "Текущий пароль указан неверно"

        new_password_errors = password_errors(
            new_password,
            current_user.username,
            current_user.email,
        )
        if new_password_errors:
            errors["new_password"] = new_password_errors[0]

        if (
            old_password
            and new_password
            and check_password_hash(current_user.password, new_password)
        ):
            errors["new_password"] = "Новый пароль должен отличаться от текущего"

        if new_password != confirm_password:
            errors["confirm_password"] = "Пароли не совпадают"

        if errors:
            return render_template("change_password.html", errors=errors)

        current_user.password = generate_password_hash(
            new_password, method="pbkdf2:sha256"
        )
        current_user.must_change_password = False

        db.session.commit()
        remember_password_version(current_user)

        flash("Пароль успешно изменён 🔐", "success")

        return redirect(url_for("profile"))

    return render_template("change_password.html", errors={})


@app.route("/cancel_my_request/<int:request_id>", methods=["POST"])
@login_required
def cancel_my_request(request_id):
    adoption = db.get_or_404(AdoptionRequest, request_id)
    db.session.execute(
        db.select(Cat).where(Cat.id == adoption.cat_id).with_for_update()
    ).scalar_one()
    db.session.refresh(adoption)

    if adoption.user_id != current_user.id:
        abort(403)

    current_status = (adoption.status or "").strip()
    cancellable = {"Новая", "На рассмотрении"}

    if current_status not in cancellable:
        flash("Эту заявку уже нельзя отменить.", "warning")

        return redirect(url_for("profile"))

    adoption.status = "Отменена"

    db.session.commit()

    flash("Заявка отменена", "success")

    return redirect(url_for("profile"))


@app.route("/favorite_cat/<int:cat_id>", methods=["POST"])
@login_required
def toggle_favorite_cat(cat_id):
    return toggle_favorite(cat_id)


@app.route("/api/cats")
@login_required
def api_cats():

    cats_list = Cat.query.order_by(Cat.id.asc()).all()
    data = []

    for cat in cats_list:
        data.append(
            {
                "id": cat.id,
                "name": cat.name,
                "nickname": cat.nickname,
                "age": cat.age,
                "age_category": cat.age_category(),
                "breed": cat.breed,
                "gender": cat.gender,
                "color": cat.color,
                "weight": cat.weight,
                "mood": cat.mood,
                "status": cat.status,
                "health": cat.health,
                "description": cat.description,
                "personality": cat.personality,
                "activity_level": cat.activity_level,
                "kids_friendly": bool(cat.kids_friendly),
                "cats_friendly": bool(cat.cats_friendly),
                "dogs_friendly": bool(cat.dogs_friendly),
                "favorite_toy": cat.favorite_toy,
                "favorite_place": cat.favorite_place,
                "food_preferences": cat.food_preferences,
                "vocal": cat.vocal,
                "story": cat.story,
                "adoption_recommendation": cat.adoption_recommendation,
                "photo_path": cat.photo_path,
                "arrival_date": (
                    cat.arrival_date.isoformat() if cat.arrival_date else None
                ),
                "adoption_date": (
                    cat.adoption_date.isoformat() if cat.adoption_date else None
                ),
                "days_in_shelter": cat.days_in_shelter,
                "is_vaccinated": bool(cat.is_vaccinated),
                "vaccination_status": cat.vacc_status(),
                "last_vacc_date": (
                    cat.last_vacc_date.isoformat() if cat.last_vacc_date else None
                ),
                "next_vacc_date": (
                    cat.next_vacc_date.isoformat() if cat.next_vacc_date else None
                ),
                "is_sterilized": bool(cat.is_sterilized),
                "created_at": (cat.created_at.isoformat() if cat.created_at else None),
                "updated_at": (cat.updated_at.isoformat() if cat.updated_at else None),
            }
        )

    response = jsonify({"count": len(data), "cats": data})
    response.headers["Cache-Control"] = "no-store"

    return response


@app.route("/api/stats")
@login_required
def api_stats():

    cats_list = Cat.query.all()
    total = len(cats_list)
    by_status = {}

    for cat in cats_list:
        status = cat.status or "Не указан"
        by_status[status] = by_status.get(status, 0) + 1

    vaccinated = sum(1 for cat in cats_list if cat.is_vaccinated)
    sterilized = sum(1 for cat in cats_list if cat.is_sterilized)
    attention = sum(
        1
        for cat in cats_list
        if (cat.next_vacc_date and cat.next_vacc_date < date.today())
    )
    response = jsonify(
        {
            "total": total,
            "by_status": by_status,
            "in_shelter": by_status.get("В приюте", 0),
            "adopted": by_status.get("Усыновлён", 0),
            "treatment": by_status.get("На лечении", 0),
            "quarantine": by_status.get("В карантине", 0),
            "vaccinated": vaccinated,
            "vaccinated_percent": (round(vaccinated / total * 100, 1) if total else 0),
            "sterilized": sterilized,
            "sterilized_percent": (round(sterilized / total * 100, 1) if total else 0),
            "vaccination_attention": attention,
        }
    )
    response.headers["Cache-Control"] = "no-store"

    return response


register_daily_story(app)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("icons/favicon.ico")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")

    app.run(host=host, port=port, debug=False)
