"""Check themes in Chromium using only synthetic data and temporary SQLite."""

import argparse
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server


def run(source, output):
    sys.path.insert(0, str(source))
    with tempfile.TemporaryDirectory(prefix="kotopolis-theme-") as temporary:
        os.environ.update(
            SECRET_KEY="theme-check-only",
            DATABASE_URL="sqlite:///" + (Path(temporary) / "test.sqlite").as_posix(),
            COOKIE_SECURE="false",
            RATELIMIT_ENABLED="false",
            PUBLIC_BASE_URL="http://127.0.0.1:5000",
        )
        from app import app, serializer
        from flask import abort
        from flask_migrate import upgrade
        from models import AdoptionRequest, Cat, FavoriteCat, User, db

        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        app.config.update(
            STORY_STATE_DIR=str(Path(temporary) / "story"), MAIL_SUPPRESS_SEND=True
        )
        import app as application

        application.utc_now = lambda: datetime(2026, 10, 15, 12)
        app.add_url_rule("/__theme/500", "theme_test_error", lambda: abort(500))
        with app.app_context():
            upgrade(directory=str(source / "migrations"))
            people = {}
            for name, role in (
                ("theme_user", "user"),
                ("theme_admin", "admin"),
                ("theme_pending", "user"),
            ):
                person = User(
                    username=name,
                    email=name + "@example.com",
                    role=role,
                    email_confirmed=name != "theme_pending",
                )
                person.set_password("ThemeTest123")
                db.session.add(person)
                people[name] = person
            db.session.add(
                Cat(
                    id=101,
                    name="Тестовый кот",
                    age=3,
                    status="В приюте",
                    personality="Спокойный",
                    gender="Мальчик",
                )
            )
            db.session.flush()
            db.session.add(FavoriteCat(user_id=people["theme_user"].id, cat_id=101))
            db.session.add(
                AdoptionRequest(
                    user_id=people["theme_user"].id,
                    cat_id=101,
                    adopter_name="Тестовый пользователь",
                    email="theme_user@example.com",
                    status="Новая",
                    comment="Тестовая заявка",
                )
            )
            db.session.commit()
            user = people["theme_user"]
            reset = serializer.dumps(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "password_sig": user.password[-16:],
                },
                salt="password-reset",
            )
            ticket = serializer.dumps(
                {"user_id": people["theme_pending"].id}, salt="email-code-context"
            )

        output.mkdir(parents=True, exist_ok=True)
        report = {"pages": [], "errors": [], "checks": []}
        server = make_server("127.0.0.1", 0, app, threaded=True)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                for theme in ("light", "dark"):
                    for width in (1440, 390):
                        context = browser.new_context(
                            viewport={"width": width, "height": 1000},
                            reduced_motion="reduce",
                        )
                        context.add_init_script(
                            f"localStorage.setItem('kotopolis-theme', '{theme}')"
                        )
                        context.add_init_script(
                            "document.addEventListener('DOMContentLoaded', () => { window.themeAtReady = document.documentElement.dataset.theme; }, {once: true})"
                        )
                        page = context.new_page()
                        page.on(
                            "pageerror",
                            lambda error: report["errors"].append(str(error)),
                        )

                        def visit(path, name, status=200):
                            response = page.goto(
                                origin + path, wait_until="networkidle"
                            )
                            assert response.status == status, (name, response.status)
                            expect(page.locator("html")).to_have_attribute(
                                "data-theme", theme
                            )
                            expect(page.locator("#theme-toggle")).to_be_visible()
                            expect(page.locator("#theme-toggle")).to_have_attribute(
                                "aria-pressed", str(theme == "dark").lower()
                            )
                            expect(
                                page.locator(
                                    ".kp-theme-sun"
                                    if theme == "dark"
                                    else ".kp-theme-moon"
                                )
                            ).to_be_visible()
                            assert not page.evaluate(
                                "document.documentElement.scrollWidth > innerWidth"
                            ), name
                            info = page.evaluate(
                                """() => ({body: getComputedStyle(document.body).backgroundImage,
                                images: [...document.images].map(i => ({src: i.getAttribute('src'), filter: getComputedStyle(i).filter})),
                                themeBeforeDOMContentLoaded: window.themeAtReady})"""
                            )
                            assert all(
                                i["filter"] == "none" for i in info["images"]
                            ), name
                            assert info["themeBeforeDOMContentLoaded"] == theme
                            info["heading_contrast"] = page.locator(
                                "h1, h2, h3, label"
                            ).evaluate_all(
                                """items => {
                                const rgb = value => (value.match(/[\\d.]+/g) || []).map(Number);
                                const luminance = c => c.slice(0, 3).map(v => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
                                return items.filter(el => el.getBoundingClientRect().width && getComputedStyle(el).visibility !== 'hidden').map(el => {
                                    const fg = rgb(getComputedStyle(el).color);
                                    let bg = [36, 38, 45], gradient = false;
                                    for (let node = el; node && node !== document.body; node = node.parentElement) {
                                        const style = getComputedStyle(node), color = rgb(style.backgroundColor);
                                        if (style.backgroundImage !== 'none') { gradient = true; break; }
                                        if (color.length >= 3 && (color.length === 3 || color[3] === 1)) { bg = color; break; }
                                    }
                                    const a = luminance(fg), b = luminance(bg);
                                    return {text: el.textContent.trim().slice(0, 80), ratio: (Math.max(a, b) + .05) / (Math.min(a, b) + .05), approximate: gradient};
                                });
                            }"""
                            )
                            report["pages"].append(
                                {
                                    "name": name,
                                    "theme": theme,
                                    "width": width,
                                    "status": status,
                                    **info,
                                }
                            )
                            page.screenshot(
                                path=str(output / f"{theme}-{width}-{name}.png"),
                                full_page=True,
                            )

                        def signout():
                            button = page.locator('form[action="/logout"] button')
                            if not button.is_visible():
                                page.locator(".navbar-toggler").click()
                                expect(button).to_be_visible()
                                page.screenshot(
                                    path=str(output / f"{theme}-{width}-menu.png"),
                                    full_page=True,
                                )
                            button.click()
                            page.wait_for_url("**/login")

                        for path, name in (
                            ("/login", "login"),
                            ("/register", "register"),
                            ("/forgot_password", "forgot-password"),
                            ("/resend_confirmation", "resend-confirmation"),
                            ("/reset_password/" + reset, "reset-password"),
                            ("/verify_email?ticket=" + ticket, "verify-email"),
                        ):
                            visit(path, name)
                        visit("/login", "login-csrf")
                        page.evaluate(
                            "fetch('/login', {method:'POST'}).then(r=>r.text()).then(html=>{document.open();document.write(html);document.close()})"
                        )
                        page.get_by_role("heading", name="Форма устарела").wait_for(
                            state="visible"
                        )
                        page.screenshot(
                            path=str(output / f"{theme}-{width}-csrf.png"),
                            full_page=True,
                        )
                        visit("/login", "guest-login")
                        page.locator('form[action="/guest_login"] button').click()
                        page.wait_for_url("**/dashboard")
                        for path, name in (
                            ("/dashboard", "guest-dashboard"),
                            ("/cats", "guest-cats"),
                            ("/cat/101", "guest-cat"),
                        ):
                            visit(path, name)
                        signout()

                        def signin(name):
                            page.goto(origin + "/login", wait_until="networkidle")
                            page.locator("#login-identity").fill(name)
                            page.locator("#login-password").fill("ThemeTest123")
                            page.locator("button[name=submit]").click()
                            page.wait_for_url("**/dashboard")

                        signin("theme_user")
                        for path, name in (
                            ("/dashboard", "dashboard"),
                            ("/cats", "cats"),
                            ("/cat/101", "cat"),
                            ("/favorites", "favorites"),
                            ("/profile", "profile"),
                            ("/edit_profile", "edit-profile"),
                            ("/change_password", "change-password"),
                            ("/cat/101/adopt", "adoption-form"),
                        ):
                            visit(path, name)
                        response = page.goto(
                            origin + "/users", wait_until="networkidle"
                        )
                        assert response.status == 403
                        report["checks"].append(
                            "Unchanged Werkzeug 403 response (not a site template)"
                        )
                        page.goto(origin + "/profile", wait_until="networkidle")
                        signout()
                        signin("theme_admin")
                        for path, name in (
                            ("/users", "users"),
                            ("/add_cat", "add-cat"),
                            ("/edit_cat/101", "edit-cat"),
                            ("/adoption_requests", "requests"),
                            ("/exports", "exports"),
                        ):
                            visit(path, name)
                        visit("/missing", "404", 404)
                        visit("/__theme/500", "500", 500)
                        visit("/users", "users-modal-host")
                        page.locator('[data-bs-target="#createUserModal"]').click()
                        expect(page.locator("#createUserModal")).to_be_visible()
                        expect(page.locator("#theme-toggle")).to_be_hidden()
                        page.screenshot(
                            path=str(output / f"{theme}-{width}-modal.png"),
                            full_page=True,
                        )
                        hit = page.locator("#createUserModal .btn-close").evaluate(
                            "el => { const r = el.getBoundingClientRect(); return document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2).className; }"
                        )
                        report["checks"].append(
                            {
                                "modal_close_hit_target": hit,
                                "theme": theme,
                                "width": width,
                            }
                        )
                        page.keyboard.press("Escape")
                        expect(page.locator("#theme-toggle")).to_be_visible()
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        assert page.locator("#theme-toggle").bounding_box()["y"] < 1000
                        report["checks"].append(
                            f"{theme}/{width}: modal, mobile layout, scroll, images"
                        )
                        page.evaluate(
                            """() => {
                            document.querySelector('main').innerHTML = `<section id="theme-components">
                                <h1>Проверка компонентов</h1>
                                <div class="alert alert-success">Успешная операция</div>
                                <div class="alert alert-warning">Предупреждение</div>
                                <div class="alert alert-danger">Ошибка</div>
                                <div class="alert alert-info">Информация</div>
                                <div class="alert alert-secondary">Дополнительная информация</div>
                                <div class="table-responsive"><table class="table table-striped table-hover">
                                <thead><tr><th>Котик</th><th>Статус</th></tr></thead>
                                <tbody><tr><td>Тестовый кот</td><td>В приюте</td></tr><tr><td>Другой кот</td><td>Дома</td></tr></tbody></table></div>
                                <label for="theme-fixture-input">Поле ввода</label>
                                <input id="theme-fixture-input" class="form-control" placeholder="Подсказка">
                                <input class="form-control mt-2" value="Недоступное поле" disabled>
                                <select class="form-select mt-2" aria-label="Выбор"><option>Первый вариант</option><option>Второй вариант</option></select>
                                <textarea class="form-control mt-2" aria-label="Комментарий">Текст комментария</textarea>
                                <div class="dropdown-menu show mt-2" style="position:static"><a class="dropdown-item" href="#">Пункт меню</a></div>
                                <button class="btn btn-outline-pink mt-2" id="theme-hover">Наведение</button>
                            </section>`;
                            window.scrollTo(0, 0);
                        }"""
                        )
                        page.locator("#theme-hover").hover()
                        page.screenshot(
                            path=str(output / f"{theme}-{width}-components.png"),
                            full_page=True,
                        )
                        report["checks"].append(
                            f"{theme}/{width}: synthetic tables, alerts, dropdown, disabled input, textarea, hover"
                        )
                        context.close()

                context = browser.new_context()
                page = context.new_page()
                page.goto(origin + "/login", wait_until="networkidle")
                expect(page.locator("html")).to_have_attribute("data-theme", "light")
                page.evaluate("window.themeNoReload = 123")
                page.locator("#theme-toggle").click()
                assert page.evaluate("window.themeNoReload") == 123
                assert (
                    page.evaluate("localStorage.getItem('kotopolis-theme')") == "dark"
                )
                page.reload(wait_until="networkidle")
                expect(page.locator("html")).to_have_attribute("data-theme", "dark")
                page.goto(origin + "/register", wait_until="networkidle")
                expect(page.locator("html")).to_have_attribute("data-theme", "dark")
                second = context.new_page()
                second.goto(origin + "/login", wait_until="networkidle")
                page.locator("#theme-toggle").click()
                expect(second.locator("html")).to_have_attribute("data-theme", "light")
                page.evaluate("localStorage.setItem('kotopolis-theme', 'invalid')")
                page.reload(wait_until="networkidle")
                expect(page.locator("html")).to_have_attribute("data-theme", "light")
                page.locator("#theme-toggle").focus()
                page.keyboard.press("Space")
                expect(page.locator("html")).to_have_attribute("data-theme", "dark")
                state = context.storage_state()
                context.close()
                restored = browser.new_context(storage_state=state)
                page = restored.new_page()
                page.goto(origin + "/login", wait_until="networkidle")
                expect(page.locator("html")).to_have_attribute("data-theme", "dark")
                restored.close()
                blocked = browser.new_context()
                blocked.add_init_script(
                    "Storage.prototype.getItem = Storage.prototype.setItem = () => { throw new Error('blocked'); }"
                )
                page = blocked.new_page()
                page.goto(origin + "/login", wait_until="networkidle")
                page.locator("#theme-toggle").click()
                expect(page.locator("html")).to_have_attribute("data-theme", "dark")
                blocked.close()
                report["checks"].extend(
                    [
                        "default light",
                        "no reload",
                        "persistence",
                        "navigation",
                        "cross-tab sync",
                        "invalid value",
                        "keyboard",
                        "reopened context",
                        "blocked storage",
                    ]
                )
                assert not report["errors"], report["errors"]
                browser.close()
        finally:
            server.shutdown()
            worker.join(timeout=5)
            with app.app_context():
                db.session.remove()
                db.engine.dispose()
            (output / "theme-results.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        print(
            f"Theme checks: {len(report['pages'])} pages, {len(report['checks'])} scenarios, {len(report['errors'])} JS errors"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source.resolve(), args.output.resolve())
