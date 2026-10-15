"""Check the login layout and theme control using temporary local data."""

import argparse
from hashlib import sha256
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server


def run(output):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    output.mkdir(parents=True, exist_ok=True)
    report = {"pages": [], "errors": []}
    with tempfile.TemporaryDirectory(prefix="kotopolis-mobile-") as temporary:
        os.environ.update(
            SECRET_KEY="mobile-layout-test-only",
            DATABASE_URL="sqlite:///" + (Path(temporary) / "test.sqlite").as_posix(),
            COOKIE_SECURE="false",
            RATELIMIT_ENABLED="false",
        )
        from app import app
        from flask_migrate import upgrade
        from models import Cat, User, db

        app.config.update(
            STORY_STATE_DIR=str(Path(temporary) / "story"), MAIL_SUPPRESS_SEND=True
        )
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        identities = {"public": None}
        with app.app_context():
            upgrade(directory=str(source / "migrations"))
            for role in ("user", "admin"):
                user = User(
                    username="mobile_" + role,
                    email=role + "@example.com",
                    role=role,
                    email_confirmed=True,
                )
                user.set_password("MobileLayout123")
                db.session.add(user)
                db.session.flush()
                identities[role] = app.session_interface.get_signing_serializer(
                    app
                ).dumps(
                    {
                        "_user_id": str(user.id),
                        "_fresh": True,
                        "password_version": sha256(user.password.encode()).hexdigest(),
                    }
                )
            db.session.add(Cat(id=101, name="Тестовый кот", status="В приюте"))
            db.session.commit()
        paths = {
            "public": ["/login", "/register", "/forgot_password", "/missing"],
            "user": [
                "/dashboard",
                "/cats",
                "/cat/101",
                "/favorites",
                "/profile",
                "/edit_profile",
                "/change_password",
                "/cat/101/adopt",
            ],
            "admin": [
                "/users",
                "/add_cat",
                "/edit_cat/101",
                "/adoption_requests",
                "/exports",
            ],
        }
        server = make_server("127.0.0.1", 0, app, threaded=True)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as playwright:
                for engine in ("chromium", "webkit"):
                    browser = getattr(playwright, engine).launch()
                    for theme in ("light", "dark"):
                        for role, cookie in identities.items():
                            context = browser.new_context(reduced_motion="reduce")
                            context.add_init_script(
                                f"localStorage.setItem('kotopolis-theme', '{theme}')"
                            )
                            if cookie:
                                context.add_cookies(
                                    [
                                        {
                                            "name": app.config["SESSION_COOKIE_NAME"],
                                            "value": cookie,
                                            "url": origin,
                                        }
                                    ]
                                )
                            page = context.new_page()
                            page.on(
                                "pageerror",
                                lambda error: report["errors"].append(str(error)),
                            )
                            widths = (
                                (320, 360, 375, 390, 414, 430, 1440)
                                if role == "public"
                                else (320, 430, 1440)
                            )
                            for width in widths:
                                page.set_viewport_size({"width": width, "height": 844})
                                for path in paths[role]:
                                    if (
                                        role == "public"
                                        and path != "/login"
                                        and width not in (320, 430, 1440)
                                    ):
                                        continue
                                    response = page.goto(
                                        origin + path, wait_until="networkidle"
                                    )
                                    assert response.status == (
                                        404 if path == "/missing" else 200
                                    ), path
                                    expect(page.locator("html")).to_have_attribute(
                                        "data-theme", theme
                                    )
                                    assert not page.evaluate(
                                        "document.documentElement.scrollWidth > innerWidth"
                                    ), (engine, width, path)
                                    toggle = page.locator("#theme-toggle")
                                    expect(toggle).to_be_visible()
                                    if width < 768:
                                        assert page.evaluate(
                                            """() => {
                                            const t = document.querySelector('#theme-toggle').getBoundingClientRect();
                                            const n = document.querySelector('nav').getBoundingClientRect();
                                            return t.top >= n.top && t.bottom <= n.bottom + 1;
                                        }"""
                                        ), (engine, width, path, "theme outside navbar")
                                    if path == "/login":
                                        assert page.evaluate(
                                            """() => {
                                            const image = document.querySelector('.kp-auth3-cat-gif');
                                            const r = image.getBoundingClientRect();
                                            const title = document.querySelector('.kp-auth3-scene-copy h2').getBoundingClientRect();
                                            return image.complete && image.naturalWidth > 0 &&
                                                (innerWidth >= 768 || (r.width <= 90 && r.left >= title.right - 1));
                                        }"""
                                        ), (engine, width, "GIF overlaps text")
                                        submit = page.locator('button[name="submit"]')
                                        submit.scroll_into_view_if_needed()
                                        assert submit.evaluate(
                                            """el => {
                                            const r = el.getBoundingClientRect();
                                            return el.contains(document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2));
                                        }"""
                                        ), (engine, width, "login blocked")
                                        page.evaluate("scrollTo(0, 0)")
                                        page.screenshot(
                                            path=str(
                                                output
                                                / f"{engine}-{theme}-{width}-login.png"
                                            ),
                                            full_page=True,
                                        )
                                    report["pages"].append(
                                        {
                                            "engine": engine,
                                            "theme": theme,
                                            "width": width,
                                            "path": path,
                                        }
                                    )
                            context.close()
                    browser.close()
            assert not report["errors"], report["errors"]
        finally:
            server.shutdown()
            worker.join(timeout=5)
            with app.app_context():
                db.session.remove()
                db.engine.dispose()
            (output / "results.json").write_text(
                json.dumps(report, indent=2), encoding="utf-8"
            )
    print(
        f"Mobile layout: {len(report['pages'])} page checks, {len(report['errors'])} JS errors"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output.resolve())
