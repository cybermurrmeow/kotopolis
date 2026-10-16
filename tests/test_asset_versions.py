import re
from urllib.parse import parse_qs, urlsplit

import pytest

from models import Cat, db
from test_app import create_user, login


def assert_asset_versions(response):
    assert response.status_code == 200
    urls = re.findall(r'(?:src|href)="([^"]+)"', response.get_data(as_text=True))
    assets = [urlsplit(url) for url in urls if url.startswith("/static/")]
    scripts_and_styles = [url for url in assets if url.path.endswith((".css", ".js"))]
    assert scripts_and_styles
    for url in scripts_and_styles:
        assert parse_qs(url.query).get("v"), url.path


@pytest.mark.parametrize(
    "path", ["/login", "/register", "/forgot_password", "/resend_confirmation"]
)
def test_public_pages_version_scripts_and_styles(client, path):
    assert_asset_versions(client.get(path))


def test_authenticated_pages_version_scripts_and_styles(client, app):
    create_user(app, "admin", "admin")
    with app.app_context():
        cat = Cat(name="Test", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id
    login(client, "admin")
    for path in (
        "/dashboard",
        "/cats",
        f"/cat/{cat_id}",
        "/favorites",
        "/profile",
        "/edit_profile",
        "/change_password",
        "/users",
        "/add_cat",
        f"/edit_cat/{cat_id}",
        "/adoption_requests",
        "/exports",
    ):
        assert_asset_versions(client.get(path))
