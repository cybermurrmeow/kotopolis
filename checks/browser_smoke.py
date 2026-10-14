"""Run real Chromium checks against an isolated local server with synthetic data."""

import argparse
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server


def run(source, output, visual_only=False):
    sys.path.insert(0, str(source))
    with tempfile.TemporaryDirectory(prefix="kotopolis-browser-") as temporary:
        os.environ.update(
            SECRET_KEY="browser-test-only",
            DATABASE_URL="sqlite:///"
            + str(Path(temporary) / "test.sqlite").replace("\\", "/"),
            COOKIE_SECURE="false",
            RATELIMIT_ENABLED="false",
            PUBLIC_BASE_URL="http://127.0.0.1:5000",
        )
        from app import app
        from models import Cat, User, db
        from flask_migrate import upgrade

        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        app.config.update(
            STORY_STATE_DIR=str(Path(temporary) / "story"), MAIL_SUPPRESS_SEND=True
        )
        with app.app_context():
            upgrade(directory=str(source / "migrations"))
            for name, role in [("browser_user", "user"), ("browser_admin", "admin")]:
                user = User(
                    username=name,
                    email=name + "@example.com",
                    role=role,
                    email_confirmed=True,
                )
                user.set_password("BrowserTest123")
                db.session.add(user)
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
            db.session.commit()

        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        output.mkdir(parents=True, exist_ok=True)
        report = {
            "origin": origin,
            "engine": "Chromium",
            "pages": [],
            "page_errors": [],
            "external_failures": [],
            "screenshots": [],
        }
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                context = browser.new_context(
                    viewport={"width": 1440, "height": 1000}, reduced_motion="reduce"
                )
                page = context.new_page()
                page.on(
                    "pageerror", lambda error: report["page_errors"].append(str(error))
                )
                page.on(
                    "requestfailed",
                    lambda request: (
                        report["external_failures"].append(request.url)
                        if not request.url.startswith(origin)
                        else None
                    ),
                )

                def visit(path, expected=200):
                    response = page.goto(origin + path, wait_until="networkidle")
                    assert response.status == expected, (path, response.status)
                    assert page.locator("title script").count() == 0
                    report["pages"].append(
                        {
                            "path": path,
                            "status": response.status,
                            "width": page.viewport_size["width"],
                            "overflow": page.evaluate(
                                "document.documentElement.scrollWidth > window.innerWidth"
                            ),
                        }
                    )

                def signin(name):
                    visit("/login")
                    page.locator("#login-identity").fill(name)
                    page.locator("#login-password").fill("BrowserTest123")
                    page.locator("button[name=submit]").click()
                    page.wait_for_url("**/dashboard")

                visit("/login")
                page.locator('form[action="/guest_login"] button').click()
                page.wait_for_url("**/dashboard")
                visit("/cats")
                visit("/cat/101")
                page.locator('form[action="/logout"] button').click()
                page.wait_for_url("**/login")

                signin("browser_user")
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    for path in (
                        "/dashboard",
                        "/cats",
                        "/cat/101",
                        "/profile",
                        "/edit_profile",
                        "/change_password",
                        "/cat/101/adopt",
                    ):
                        visit(path)
                        screenshot = f"{width}-{path.strip('/').replace('/', '-')}.png"
                        page.screenshot(path=str(output / screenshot), full_page=True)
                        report["screenshots"].append(screenshot)
                    visit("/edit_profile")
                    warning = page.locator("#emailChangeWarning")
                    assert warning.is_hidden()
                    page.locator("#email").fill("changed@example.com")
                    assert warning.is_visible()

                if visual_only:
                    assert not report["page_errors"], report["page_errors"]
                    browser.close()
                    return

                page.set_viewport_size({"width": 1440, "height": 1000})
                visit("/cats")
                page.locator('form[action="/favorite/101"] button').click()
                expect(
                    page.locator('form[action="/favorite/101"] button')
                ).to_have_attribute("aria-pressed", "true")
                visit("/favorites")
                page.locator('form[action="/favorite/101"] button').click()
                page.locator(".kp-favorites-empty").wait_for(state="visible")
                visit("/users", expected=403)
                visit("/profile")
                page.locator('form[action="/logout"] button').click()
                page.wait_for_url("**/login")
                signin("browser_admin")
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    for path in (
                        "/users",
                        "/add_cat",
                        "/edit_cat/101",
                        "/adoption_requests",
                        "/exports",
                    ):
                        visit(path)
                        screenshot = (
                            f"{width}-admin-{path.strip('/').replace('/', '-')}.png"
                        )
                        page.screenshot(path=str(output / screenshot), full_page=True)
                        report["screenshots"].append(screenshot)
                assert not report["page_errors"], report["page_errors"]
                assert not any(
                    item["overflow"] for item in report["pages"]
                ), "Horizontal overflow detected"
                browser.close()
        finally:
            server.shutdown()
            thread.join(timeout=5)
            with app.app_context():
                db.session.remove()
                db.engine.dispose()
            (output / "browser-results.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        print(
            f"Browser: {len(report['pages'])} page checks; {len(report['page_errors'])} JS errors; results at {output}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--visual-only", action="store_true")
    args = parser.parse_args()
    run(args.source.resolve(), args.output.resolve(), args.visual_only)
