import os
from datetime import date, datetime, timedelta
from io import BytesIO
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from models import db, User, Cat, AdoptionRequest, CatComment
from forms import LoginForm, RegisterForm, CatForm, AdoptionForm, CommentForm, ForgotPasswordForm, SetupSecurityForm
from utils import export_to_excel, generate_pdf_report, calculate_stats


# ====================== ДЕКОРАТОР ДЛЯ АДМИНА ======================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('🌸 Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            flash('🩷 У вас нет прав для выполнения этого действия', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ====================== СОЗДАНИЕ ПРИЛОЖЕНИЯ ======================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kotopolis_pink_secret_key_2026_updated'

# ========== НАСТРОЙКА БАЗЫ ДАННЫХ (для разных платформ) ==========
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///kotopolis.db')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ========== НАСТРОЙКИ ДЛЯ СТАБИЛЬНОГО СОЕДИНЕНИЯ С POSTGRESQL ==========
# Настройки для Supabase
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
    'pool_size': 5,
    'max_overflow': 10,
    'connect_args': {
        'sslmode': 'require'
    }
}

# ========== НАСТРОЙКИ EMAIL ==========
app.config['MAIL_SERVER'] = 'smtp.rambler.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kotopolis.cat@rambler.ru'
app.config['MAIL_PASSWORD'] = 'Dsm-L88-G93-tXa'
app.config['MAIL_DEFAULT_SENDER'] = 'kotopolis.cat@rambler.ru'
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['TESTING'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# ========== ИНИЦИАЛИЗАЦИЯ EMAIL ==========
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '🌸 Пожалуйста, войдите в систему для доступа к этой странице'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Ошибка загрузки пользователя: {e}")
        return None


def send_confirmation_email(user):
    """Отправляет письмо с подтверждением email"""
    token = serializer.dumps(user.email, salt='email-confirm')
    confirm_url = url_for('confirm_email', token=token, _external=True)
    
    msg = Message("🐱 Подтверждение email - Котополис", recipients=[user.email])
    msg.html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Подтверждение email - Котополис</title>
    </head>
    <body style="font-family: 'Segoe UI', 'Quicksand', Arial, sans-serif; background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%); padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 30px; padding: 30px; box-shadow: 0 10px 30px rgba(255, 105, 180, 0.15);">
            <div style="text-align: center;">
                <div style="font-size: 48px;">🐱💕</div>
                <h1 style="color: #FF69B4; margin-bottom: 10px;">Котополис</h1>
                <h2 style="color: #FF1493; font-size: 20px;">Подтверждение email</h2>
            </div>
            
            <p>Здравствуйте, <strong style="color: #FF69B4;">{user.username}</strong>!</p>
            
            <p>Спасибо за регистрацию в <strong style="color: #FF69B4;">Котополисе</strong> — розовом рае для котиков! 🐱</p>
            
            <p>Для завершения регистрации и входа в систему, пожалуйста, подтвердите ваш email, нажав на кнопку ниже:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{confirm_url}" style="background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 50px; display: inline-block; box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3);">
                    🩷 Подтвердить email
                </a>
            </div>
            
            <p>Или скопируйте ссылку в браузер:</p>
            <p style="background: linear-gradient(135deg, #FFF0F5 0%, #FFE8EE 100%); padding: 10px; border-radius: 15px; word-break: break-all; font-size: 12px;">
                {confirm_url}
            </p>
            
            <p>🌸 Ссылка действительна в течение 1 часа.</p>
            
            <hr style="margin: 20px 0; border: none; height: 2px; background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%);">
            
            <p style="color: #9B7B7B; font-size: 12px; text-align: center;">
                <i class="fas fa-heart"></i> Если вы не регистрировались в Котополисе, просто проигнорируйте это письмо.
            </p>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)
    
    print(f"✅ Письмо с подтверждением отправлено на {user.email}")


def send_password_reset_email(user):
    """Отправляет письмо для сброса пароля"""
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    
    msg = Message("🔐 Сброс пароля - Котополис", recipients=[user.email])
    msg.html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Сброс пароля - Котополис</title>
    </head>
    <body style="font-family: 'Segoe UI', 'Quicksand', Arial, sans-serif; background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%); padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 30px; padding: 30px; box-shadow: 0 10px 30px rgba(255, 105, 180, 0.15);">
            <div style="text-align: center;">
                <div style="font-size: 48px;">🐱🔐</div>
                <h1 style="color: #FF69B4; margin-bottom: 10px;">Котополис</h1>
                <h2 style="color: #FF1493; font-size: 20px;">Сброс пароля</h2>
            </div>
            
            <p>Здравствуйте, <strong style="color: #FF69B4;">{user.username}</strong>!</p>
            
            <p>Вы запросили сброс пароля в <strong style="color: #FF69B4;">Котополисе</strong>.</p>
            
            <p>Для установки нового пароля нажмите на кнопку ниже:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 50px; display: inline-block; box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3);">
                    🩷 Сбросить пароль
                </a>
            </div>
            
            <p>Или скопируйте ссылку в браузер:</p>
            <p style="background: linear-gradient(135deg, #FFF0F5 0%, #FFE8EE 100%); padding: 10px; border-radius: 15px; word-break: break-all; font-size: 12px;">
                {reset_url}
            </p>
            
            <p>🌸 Ссылка действительна в течение 1 часа.</p>
            
            <hr style="margin: 20px 0; border: none; height: 2px; background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%);">
            
            <p style="color: #9B7B7B; font-size: 12px; text-align: center;">
                <i class="fas fa-heart"></i> Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
            </p>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)
    
    print(f"✅ Письмо для сброса пароля отправлено на {user.email}")


# ====================== МАРШРУТЫ ======================
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Проверка паролей
        if form.password.data != form.confirm_password.data:
            flash('🌸 Пароли не совпадают!', 'danger')
            return render_template('register.html', form=form)

        username_raw = form.username.data.strip()
        if not username_raw or len(username_raw) < 3:
            flash('🐱 Логин должен содержать минимум 3 символа', 'danger')
            return render_template('register.html', form=form)

        username_lower = username_raw.lower()

        if User.query.filter_by(username=username_lower).first():
            flash('🐱 Пользователь с таким логином уже существует. Придумайте другой.', 'danger')
            return render_template('register.html', form=form)

        email = form.email.data.strip().lower() if form.email.data else None

        if not email:
            flash('📧 Email обязателен для регистрации', 'danger')
            return render_template('register.html', form=form)

        new_user = User(
            username=username_lower,
            email=email,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
            role='user',
            email_confirmed=False
        )
        
        # Временно убрали try/except, чтобы видеть настоящую ошибку
        db.session.add(new_user)
        db.session.commit()
        
        send_confirmation_email(new_user)
        
        flash('🎉 Регистрация прошла успешно! Проверьте почту для подтверждения email. 🩷', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.username_or_email.data.strip()
        
        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()
        
        if user and check_password_hash(user.password, form.password.data):
            if not user.email_confirmed:
                flash('⚠️ Подтвердите email перед входом! Проверьте почту. 📧', 'warning')
                return render_template('login.html', form=form)
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash(f'🐱 Добро пожаловать в Котополис, {user.username}! 🩷', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('welcome'))
        else:
            flash('❌ Неверный логин/email или пароль', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 До скорых встреч в Котополисе! 🩷', 'info')
    return redirect(url_for('login'))


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('🌸 Ссылка подтверждения недействительна или истекла', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('🐱 Пользователь не найден', 'danger')
        return redirect(url_for('login'))
    
    if user.email_confirmed:
        flash('📧 Email уже был подтвержден', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_at = datetime.utcnow()
        db.session.commit()
        flash('✅ Email успешно подтвержден! Теперь вы можете войти в Котополис. 🩷', 'success')
    
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    cats = Cat.query.all()
    stats = calculate_stats(cats)
    
    today = date.today()
    need_vacc = []
    for cat in cats:
        if not cat.last_vacc_date:
            need_vacc.append(cat)
        elif (today - cat.last_vacc_date).days > 365:
            need_vacc.append(cat)
    
    recent_cats = Cat.query.order_by(Cat.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats,
                         need_vacc=need_vacc,
                         recent_cats=recent_cats,
                         cats=cats)


@app.route('/cats')
@login_required
def cats():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    mood = request.args.get('mood', '')
    gender = request.args.get('gender', '')
    personality = request.args.get('personality', '')
    activity_level = request.args.get('activity_level', '')
    vocal = request.args.get('vocal', '')
    sort = request.args.get('sort', 'name')
    
    query = Cat.query
    
    if search:
        query = query.filter(
            Cat.name.ilike(f'%{search}%') | 
            Cat.nickname.ilike(f'%{search}%') |
            Cat.breed.ilike(f'%{search}%')
        )
    
    if status:
        query = query.filter_by(status=status)
    if mood:
        query = query.filter_by(mood=mood)
    if gender:
        query = query.filter_by(gender=gender)
    if personality:
        query = query.filter_by(personality=personality)
    if activity_level:
        query = query.filter_by(activity_level=activity_level)
    if vocal:
        query = query.filter_by(vocal=vocal)
    
    if sort == 'age_asc':
        query = query.order_by(Cat.age)
    elif sort == 'age_desc':
        query = query.order_by(Cat.age.desc())
    elif sort == 'arrival_desc':
        query = query.order_by(Cat.arrival_date.desc())
    elif sort == 'arrival_asc':
        query = query.order_by(Cat.arrival_date)
    elif sort == 'name_desc':
        query = query.order_by(Cat.name.desc())
    else:
        query = query.order_by(Cat.name)
    
    cats = query.all()
    
    all_statuses = ['В приюте', 'Усыновлён', 'На лечении', 'В карантине']
    all_moods = ['Весёлое', 'Спокойное', 'Игривое', 'Грустное']
    all_genders = ['Мальчик', 'Девочка']
    all_personalities = ['Ласковый', 'Игривый', 'Спокойный', 'Независимый', 'Пугливый', 'Энергичный', 'Добрый']
    all_activity_levels = ['Высокий', 'Средний', 'Низкий']
    all_vocals = ['Молчаливый', 'Разговорчивый', 'Поющий', 'Мяукает редко']
    
    return render_template('cats.html', 
                         cats=cats, 
                         search=search, 
                         status=status,
                         mood=mood,
                         gender=gender,
                         personality=personality,
                         activity_level=activity_level,
                         vocal=vocal,
                         sort=sort,
                         all_statuses=all_statuses,
                         all_moods=all_moods,
                         all_genders=all_genders,
                         all_personalities=all_personalities,
                         all_activity_levels=all_activity_levels,
                         all_vocals=all_vocals)


@app.route('/cat/<int:cat_id>')
@login_required
def cat_details(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CommentForm()
    adoption_form = AdoptionForm()
    comments = CatComment.query.filter_by(cat_id=cat_id).order_by(CatComment.created_at.desc()).all()
    
    adoption_request = AdoptionRequest.query.filter_by(cat_id=cat_id, email=current_user.email).first()
    
    return render_template('cat_details.html', 
                         cat=cat, 
                         form=form, 
                         adoption_form=adoption_form,
                         comments=comments,
                         adoption_request=adoption_request)


@app.route('/add_cat', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cat():
    form = CatForm()
    if form.validate_on_submit():
        photo_path = None
        
        if form.gif_url.data:
            photo_path = form.gif_url.data
        elif form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            if not filename.lower().endswith('.gif'):
                flash('❌ Можно загружать только GIF-файлы! 🐱', 'danger')
                return render_template('add_cat.html', form=form)
            
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{name_parts[1]}"
            photo_path = f'uploads/{filename}'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_cat = Cat(
            name=form.name.data,
            nickname=form.nickname.data,
            age=form.age.data,
            breed=form.breed.data,
            gender=form.gender.data,
            color=form.color.data,
            weight=form.weight.data,
            mood=form.mood.data,
            favorite_toy=form.favorite_toy.data,
            arrival_date=form.arrival_date.data or date.today(),
            status=form.status.data,
            health=form.health.data,
            description=form.description.data,
            last_vacc_date=form.last_vacc_date.data or date.today(),
            next_vacc_date=form.next_vacc_date.data,
            adoption_date=form.adoption_date.data,
            is_vaccinated=form.is_vaccinated.data,
            is_sterilized=form.is_sterilized.data,
            photo_path=photo_path,
            personality=form.personality.data,
            activity_level=form.activity_level.data,
            kids_friendly=form.kids_friendly.data,
            cats_friendly=form.cats_friendly.data,
            dogs_friendly=form.dogs_friendly.data,
            favorite_place=form.favorite_place.data,
            vocal=form.vocal.data,
            food_preferences=form.food_preferences.data,
            story=form.story.data,
            adoption_recommendation=form.adoption_recommendation.data
        )
        
        try:
            new_cat.validate_photo()
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('add_cat.html', form=form)
        
        db.session.add(new_cat)
        db.session.commit()
        
        flash(f'🐱 Котик {new_cat.name} успешно добавлен в Котополис! 🩷', 'success')
        return redirect(url_for('cats'))
    
    return render_template('add_cat.html', form=form)


@app.route('/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cat(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CatForm(obj=cat)
    
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.nickname = form.nickname.data
        cat.age = form.age.data
        cat.breed = form.breed.data
        cat.gender = form.gender.data
        cat.color = form.color.data
        cat.weight = form.weight.data
        cat.mood = form.mood.data
        cat.favorite_toy = form.favorite_toy.data
        cat.arrival_date = form.arrival_date.data
        cat.status = form.status.data
        cat.health = form.health.data
        cat.description = form.description.data
        cat.last_vacc_date = form.last_vacc_date.data
        cat.next_vacc_date = form.next_vacc_date.data
        cat.adoption_date = form.adoption_date.data
        cat.is_vaccinated = form.is_vaccinated.data
        cat.is_sterilized = form.is_sterilized.data
        
        cat.personality = form.personality.data
        cat.activity_level = form.activity_level.data
        cat.kids_friendly = form.kids_friendly.data
        cat.cats_friendly = form.cats_friendly.data
        cat.dogs_friendly = form.dogs_friendly.data
        cat.favorite_place = form.favorite_place.data
        cat.vocal = form.vocal.data
        cat.food_preferences = form.food_preferences.data
        cat.story = form.story.data
        cat.adoption_recommendation = form.adoption_recommendation.data
        
        if form.gif_url.data:
            cat.photo_path = form.gif_url.data
        elif form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            if not filename.lower().endswith('.gif'):
                flash('❌ Можно загружать только GIF-файлы!', 'danger')
                return render_template('edit_cat.html', form=form, cat=cat)
            
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{name_parts[1]}"
            photo_path = f'uploads/{filename}'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cat.photo_path = photo_path
        
        cat.updated_at = datetime.utcnow()
        
        try:
            cat.validate_photo()
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('edit_cat.html', form=form, cat=cat)
        
        db.session.commit()
        
        flash(f'✅ Данные котика {cat.name} обновлены! 🩷', 'success')
        return redirect(url_for('cat_details', cat_id=cat.id))
    
    return render_template('edit_cat.html', form=form, cat=cat)


@app.route('/delete_cat/<int:cat_id>')
@login_required
@admin_required
def delete_cat(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    cat_name = cat.name
    
    if cat.photo_path:
        try:
            photo_full_path = os.path.join('static', cat.photo_path)
            if os.path.exists(photo_full_path):
                os.remove(photo_full_path)
        except Exception as e:
            print(f"Ошибка при удалении фото: {e}")
    
    db.session.delete(cat)
    db.session.commit()
    flash(f'🗑️ Котик {cat_name} удалён из базы', 'warning')
    return redirect(url_for('cats'))


@app.route('/add_comment/<int:cat_id>', methods=['POST'])
@login_required
def add_comment(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = CatComment(
            cat_id=cat_id,
            user_id=current_user.id,
            comment=form.comment.data
        )
        db.session.add(comment)
        db.session.commit()
        flash('💬 Комментарий добавлен! 🩷', 'success')
    
    return redirect(url_for('cat_details', cat_id=cat_id))


@app.route('/adopt/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def adopt(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    
    if cat.status == 'Усыновлён':
        flash('❌ Этот котик уже усыновлён!', 'warning')
        return redirect(url_for('cat_details', cat_id=cat_id))
    
    form = AdoptionForm()
    
    if request.method == 'GET':
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        if form.email.data != current_user.email:
            flash('❌ Email должен совпадать с email вашего аккаунта!', 'danger')
            return render_template('cat_details.html', cat=cat, form=CommentForm(), adoption_form=form, comments=[], adoption_request=None)
        
        if not form.adopter_name.data or len(form.adopter_name.data.strip()) < 2:
            flash('❌ Пожалуйста, укажите ваше имя!', 'danger')
            return render_template('cat_details.html', cat=cat, form=CommentForm(), adoption_form=form, comments=[], adoption_request=None)
        
        # Проверка на повторную заявку
        existing = AdoptionRequest.query.filter_by(
            cat_id=cat_id, 
            email=form.email.data
        ).first()
        
        if existing:
            flash('📝 Вы уже подавали заявку на этого котика! Мы свяжемся с вами. 🩷', 'info')
            return redirect(url_for('cat_details', cat_id=cat_id))
        
        # ←←← ИСПРАВЛЕННЫЙ КОД ←←←
        adoption_request = AdoptionRequest(
            cat_id=cat_id,
            adopter_name=form.adopter_name.data,
            phone=form.phone.data,
            email=form.email.data,
            comment=form.comment.data,
            # user_id сюда НЕ передаём, потому что такого поля нет в модели
        )
        
        db.session.add(adoption_request)
        db.session.commit()
        
        flash(f'🩷 Спасибо! Заявка на усыновление {cat.name} отправлена. Мы свяжемся с вами в ближайшее время! 🐱', 'success')
        return redirect(url_for('cat_details', cat_id=cat_id))
    
    return render_template('cat_details.html', cat=cat, form=CommentForm(), adoption_form=form, comments=[], adoption_request=None)


@app.route('/export_excel')
@login_required
def export_excel():
    cats = Cat.query.all()
    excel_file = export_to_excel(cats)
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'kotopolis_report_{date.today()}.xlsx'
    )


@app.route('/report')
@login_required
def report():
    cats = Cat.query.all()
    pdf_file = generate_pdf_report(cats, f"Отчёт Котополис от {date.today()}")
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'kotopolis_report_{date.today()}.pdf'
    )


@app.route('/api/cats')
@login_required
def api_cats():
    cats = Cat.query.all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'age': cat.age,
        'breed': cat.breed,
        'status': cat.status,
        'mood': cat.mood,
        'photo': cat.photo_path
    } for cat in cats])


@app.route('/api/stats')
@login_required
def api_stats():
    cats = Cat.query.all()
    stats = calculate_stats(cats)
    return jsonify(stats)


@app.route('/adoption_requests')
@login_required
def adoption_requests():
    if current_user.role != 'admin':
        flash('🌸 У вас нет прав для просмотра этой страницы', 'danger')
        return redirect(url_for('dashboard'))
    
    status_filter = request.args.get('status_filter', '')
    search_cat = request.args.get('search_cat', '')
    search_user = request.args.get('search_user', '')
    sort_by = request.args.get('sort_by', 'date_desc')
    
    query = AdoptionRequest.query
    
    if status_filter and status_filter != '':
        query = query.filter(AdoptionRequest.status == status_filter)
    
    if search_cat and search_cat != '':
        query = query.join(Cat).filter(
            db.or_(
                Cat.name.ilike(f'%{search_cat}%'),
                Cat.nickname.ilike(f'%{search_cat}%')
            )
        )
    
    if search_user and search_user != '':
        query = query.filter(AdoptionRequest.adopter_name.ilike(f'%{search_user}%'))
    
    if sort_by == 'date_asc':
        query = query.order_by(AdoptionRequest.request_date.asc())
    elif sort_by == 'status':
        query = query.order_by(AdoptionRequest.status)
    else:
        query = query.order_by(AdoptionRequest.request_date.desc())
    
    requests = query.all()
    
    return render_template(
        'adoption_requests.html', 
        requests=requests,
        current_status_filter=status_filter,
        search_cat=search_cat,
        search_user=search_user,
        sort_by=sort_by
    )

@app.route('/admin/users')
@admin_required
def admin_users():
    """Страница управления пользователями (для админа)"""
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/set_role/<int:user_id>', methods=['POST'])
@admin_required
def set_role(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        flash('❌ Нельзя изменить роль главного администратора!', 'danger')
        return redirect(url_for('profile', user_id=user_id))
    
    new_role = request.form.get('role')
    
    if new_role in ['user', 'volunteer']:
        old_role = user.role
        user.role = new_role
        db.session.commit()
        flash(f'✅ Роль пользователя {user.username} изменена: {old_role} → {new_role}', 'success')
    else:
        flash('❌ Недопустимая роль', 'danger')
    
    # Важно: возвращаемся на тот же профиль, который смотрели
    return redirect(url_for('profile', user_id=user_id))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('У вас нет доступа к этому действию', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        flash('❌ Нельзя удалить главного администратора!', 'danger')
    else:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'✅ Пользователь {username} удален', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/clean-users')
@login_required
def clean_users():
    if current_user.role != 'admin':
        return "Только для админа"
    
    from app import app, db
    from models import User
    
    deleted = []
    for user in User.query.all():
        if user.role not in ['admin', 'volunteer']:
            deleted.append(user.username)
            db.session.delete(user)
    
    db.session.commit()
    return f"🗑️ Удалены: {', '.join(deleted) if deleted else 'никого'}"

@app.route('/admin/create-volunteer')
@login_required
def create_volunteer():
    if current_user.role != 'admin':
        return "Только для админа"
    
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    volunteer = User.query.filter_by(username='volunteer').first()
    
    if not volunteer:
        volunteer = User(
            username='volunteer',
            email='volunteer@kotopolis.ru',
            password=generate_password_hash('volunteer123', method='pbkdf2:sha256'),
            role='volunteer',
            email_confirmed=True,
            email_confirmed_at=datetime.utcnow()
        )
        db.session.add(volunteer)
        db.session.commit()
        return "✅ Волонтёр создан: volunteer / volunteer123"
    else:
        return "⚠️ Волонтёр уже существует"
    
@app.route('/update_request_status/<int:request_id>', methods=['POST'])
@login_required
def update_request_status(request_id):
    if current_user.role != 'admin':
        flash('🌸 У вас нет прав для этого действия', 'danger')
        return redirect(url_for('dashboard'))
    
    request_item = AdoptionRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    old_status = request_item.status
    
    if new_status in ['На рассмотрении', 'Одобрена', 'Отклонена', 'Завершена']:
        request_item.status = new_status
        db.session.commit()
        
        if new_status == 'Одобрена':
            cat = request_item.cat
            if cat and cat.status != 'Усыновлён':
                cat.status = 'Усыновлён'
                cat.adoption_date = date.today()
                db.session.commit()
                flash(f'✅ Котик {cat.name} отмечен как усыновлённый! 🩷', 'success')
        
        if old_status == 'Одобрена' and new_status != 'Одобрена':
            cat = request_item.cat
            if cat and cat.status == 'Усыновлён':
                cat.status = 'В приюте'
                cat.adoption_date = None
                db.session.commit()
                flash(f'🔄 Статус котика {cat.name} возвращён в "В приюте"', 'warning')
        
        flash(f'🩷 Статус заявки изменён на "{new_status}"', 'success')
    
    return redirect(url_for('adoption_requests'))


@app.route('/delete_request/<int:request_id>')
@login_required
def delete_request(request_id):
    if current_user.role != 'admin':
        flash('🌸 Только администратор может удалять заявки', 'danger')
        return redirect(url_for('dashboard'))
    
    request_item = AdoptionRequest.query.get_or_404(request_id)
    db.session.delete(request_item)
    db.session.commit()
    flash('🗑️ Заявка удалена', 'success')
    
    return redirect(url_for('adoption_requests'))

@app.route('/admin/migrate-cats')
@login_required
def migrate_cats():
    if current_user.role != 'admin':
        return "Только для админа"
    
    import sqlite3
    from models import Cat
    
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect('instance/kotopolis.db')
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT name, nickname, age, breed, gender, color, weight, mood, favorite_toy, status, health, description, photo_path, personality, activity_level, kids_friendly, cats_friendly, dogs_friendly, favorite_place, vocal, food_preferences, story, adoption_recommendation FROM cats")
    
    added = 0
    for row in sqlite_cursor.fetchall():
        if not Cat.query.filter_by(name=row[0]).first():
            cat = Cat(
                name=row[0], nickname=row[1], age=row[2], breed=row[3],
                gender=row[4], color=row[5], weight=row[6], mood=row[7],
                favorite_toy=row[8], status=row[9], health=row[10],
                description=row[11], photo_path=row[12], personality=row[13],
                activity_level=row[14], kids_friendly=row[15],
                cats_friendly=row[16], dogs_friendly=row[17],
                favorite_place=row[18], vocal=row[19], food_preferences=row[20],
                story=row[21], adoption_recommendation=row[22]
            )
            db.session.add(cat)
            added += 1
    
    db.session.commit()
    sqlite_conn.close()
    return f"✅ Перенесено {added} котиков из SQLite в PostgreSQL"
    
@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    if current_user.role != 'admin':
        flash('У вас нет доступа', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            email_confirmed=True,
            email_confirmed_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'✅ Пользователь {username} создан', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin_create_user.html')

@app.route('/admin/add-bio-column')
@login_required
def add_bio_column():
    if current_user.role != 'admin':
        return "Только для админа"
    
    from sqlalchemy import text
    
    with app.app_context():
        try:
            db.session.execute(text('ALTER TABLE users ADD COLUMN bio TEXT'))
            db.session.commit()
            return "✅ Колонка bio успешно добавлена!"
        except Exception as e:
            return f"⚠️ Ошибка: {e}"
        
@app.route('/test-email')
@login_required
def test_email():
    if current_user.role != 'admin':
        return "Только для админа"
    
    try:
        msg = Message(
            subject="Тестовое письмо от Котополиса",
            recipients=[current_user.email],
            body="Если вы видите это письмо — SMTP работает!"
        )
        mail.send(msg)
        return "✅ Письмо отправлено!"
    except Exception as e:
        return f"❌ Ошибка: {e}"
        

# ====================== ВОССТАНОВЛЕНИЕ ПАРОЛЯ ПО EMAIL ======================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            send_password_reset_email(user)
            flash('📧 Если такой email существует, мы отправили ссылку для сброса пароля. 🩷', 'success')
        else:
            flash('📧 Если такой email существует, мы отправили ссылку для сброса пароля. 🩷', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        flash('🌸 Ссылка для сброса пароля недействительна или истекла.', 'danger')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('🐱 Пользователь не найден', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 4:
            flash('🔐 Пароль должен содержать минимум 4 символа', 'danger')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('🌸 Пароли не совпадают', 'danger')
            return render_template('reset_password.html', token=token)
        
        if check_password_hash(user.password, password):
            flash('🩷 Новый пароль не должен совпадать со старым', 'danger')
            return render_template('reset_password.html', token=token)
        
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        
        flash('✅ Пароль успешно изменен! Теперь вы можете войти с новым паролем. 🩷', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)


# ====================== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ======================
@app.route('/profile')
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id=None):
    if user_id:
        if current_user.role != 'admin':
            flash('У вас нет доступа к чужим профилям', 'danger')
            return redirect(url_for('profile'))
        user = User.query.get_or_404(user_id)
    else:
        user = current_user
    
    return render_template('profile.html', 
                           user=user, 
                           is_admin_view=(user_id is not None and current_user.role == 'admin'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        current_user.bio = bio
        
        # Удален блок загрузки аватара
        
        db.session.commit()
        flash('✅ Профиль успешно обновлён!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(current_user.password, current_password):
            flash('❌ Неверный текущий пароль!', 'danger')
            return redirect(url_for('change_password'))
        
        if len(new_password) < 4:
            flash('❌ Новый пароль должен содержать минимум 4 символа!', 'danger')
            return redirect(url_for('change_password'))
        
        if check_password_hash(current_user.password, new_password):
            flash('❌ Новый пароль не должен совпадать со старым!', 'danger')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('❌ Пароли не совпадают!', 'danger')
            return redirect(url_for('change_password'))
        
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        
        flash('✅ Пароль успешно изменён!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')


# ====================== ДОПОЛНИТЕЛЬНЫЙ МАРШРУТ ДЛЯ ПРОВЕРКИ СТАТУСА ======================
@app.route('/health')
def health_check():
    """Простая проверка работоспособности приложения"""
    return jsonify({
        'status': 'ok',
        'message': '🐱 Котополис работает!',
        'timestamp': datetime.now().isoformat()
    })


# ====================== ОБРАБОТЧИКИ ОШИБОК ======================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    flash('🚫 У вас нет доступа к этой странице', 'danger')
    return redirect(url_for('dashboard'))


@app.errorhandler(405)
def method_not_allowed_error(error):
    flash('⚠️ Метод не поддерживается', 'warning')
    return redirect(url_for('dashboard'))

# ========== ОБРАБОТЧИК ОШИБОК БАЗЫ ДАННЫХ ==========
from sqlalchemy.exc import OperationalError

@app.errorhandler(OperationalError)
def handle_db_disconnect(e):
    db.session.rollback()
    flash('🔄 Соединение с базой данных восстановлено. Попробуйте снова.', 'warning')
    return redirect(request.url)


# ====================== КОНТЕКСТНЫЙ ПРОЦЕССОР ======================
@app.context_processor
def utility_processor():
    """Добавляет глобальные переменные во все шаблоны"""
    def get_current_year():
        return datetime.now().year
    
    def get_total_cats():
        return Cat.query.count()
    
    def get_available_cats():
        return Cat.query.filter_by(status='В приюте').count()
    
    return {
        'current_year': get_current_year(),
        'total_cats': get_total_cats(),
        'available_cats': get_available_cats(),
        'now': datetime.now()
    }


# ====================== СОЗДАНИЕ БАЗЫ ДАННЫХ ======================
with app.app_context():
    db.create_all()
    print("✅ Таблицы базы данных созданы")
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@kotopolis.ru',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin',
            email_confirmed=True,
            email_confirmed_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Администратор создан: admin / admin123")
    
    print("🐱 Котополис запущен!")

# Для Koyeb и других хостингов
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)