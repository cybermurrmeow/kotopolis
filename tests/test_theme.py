from pathlib import Path

import pytest

from test_app import create_user, login


@pytest.mark.parametrize(
    "path", ["/login", "/register", "/forgot_password", "/missing"]
)
def test_public_pages_include_theme_controls(client, path):
    html = client.get(path).get_data(as_text=True)
    assert html.count('id="theme-toggle"') == 1
    assert 'aria-label="Включить тёмную тему"' in html
    assert html.index("js/theme.js") < html.index('rel="stylesheet"')
    assert "css/theme.css" in html


@pytest.mark.parametrize("role,path", [("user", "/profile"), ("admin", "/users")])
def test_authenticated_pages_include_theme_controls(app, client, role, path):
    create_user(app, role=role)
    login(client)
    response = client.get(path)
    assert response.status_code == 200
    assert 'id="theme-toggle"' in response.get_data(as_text=True)


def test_theme_assets_are_served(client):
    for name in ("js/theme.js", "css/theme.css"):
        assert client.get("/static/" + name).status_code == 200


def test_theme_has_no_image_filters():
    css = (Path(__file__).resolve().parents[1] / "static/css/theme.css").read_text()
    assert "!important" not in css
    assert '[data-theme="dark"] img' not in css
    assert '[data-theme="dark"] video' not in css
