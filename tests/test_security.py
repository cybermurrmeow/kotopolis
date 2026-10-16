import pytest

from app import app


@pytest.mark.parametrize("url", [
    "/users",
    "/exports",
    "/export_excel",
    "/report",
])
def test_anonymous_user_cannot_access_admin_pages(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.parametrize("url", [
    "/users",
    "/exports",
    "/export_cats_csv",
    "/export_cats_excel",
    "/export_cats_pdf",
    "/export_excel",
    "/report",
])
def test_regular_user_cannot_access_admin_pages(
    logged_in_client, url
):
    client = logged_in_client(role="user")
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.parametrize("url", [
    "/users",
    "/exports",
])
def test_admin_can_access_admin_pages(logged_in_client, url):
    client = logged_in_client(role="admin")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.parametrize("url", [
    "/users/create",
    "/user/999999/role",
    "/user/999999/delete",
    "/add_cat",
    "/delete_cat/999999",
    "/adoption_request/999999/status",
    "/adoption_request/999999/delete",
])
def test_regular_user_cannot_perform_admin_actions(
    logged_in_client, url
):
    client = logged_in_client(role="user")
    response = client.post(url, data={})

    assert response.status_code == 403


@pytest.mark.parametrize("role", ["user", "admin"])
@pytest.mark.parametrize("url", [
    "/cats",
    "/users",
    "/exports",
    "/report",
])
def test_temporary_password_redirects_to_password_change(
    logged_in_client, role, url
):
    client = logged_in_client(
        role=role,
        must_change_password=True,
    )

    response = client.get(url)

    assert response.status_code == 302
    assert "/change_password" in response.headers["Location"]


@pytest.mark.parametrize("role", ["user", "admin"])
def test_password_change_page_remains_accessible(
    logged_in_client, role
):
    client = logged_in_client(
        role=role,
        must_change_password=True,
    )

    response = client.get("/change_password")

    assert response.status_code == 200


@pytest.mark.parametrize("role", ["user", "admin"])
def test_temporary_password_blocks_admin_post(
    logged_in_client, role
):
    client = logged_in_client(
        role=role,
        must_change_password=True,
    )

    response = client.post(
        "/users/create",
        data={"username": "should_not_be_created"},
    )

    assert response.status_code == 403


def test_regular_user_can_open_catalog(logged_in_client):
    client = logged_in_client(role="user")
    response = client.get("/cats")

    assert response.status_code == 200


def test_guest_cannot_open_user_management(client):
    response = client.post("/guest_login")
    assert response.status_code == 302

    response = client.get("/users")
    assert response.status_code == 302


def test_csrf_blocks_post_without_token(client):
    app.config["WTF_CSRF_ENABLED"] = True

    try:
        response = client.post("/favorite/999999")
        assert response.status_code == 400
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


@pytest.mark.parametrize("url", [
    "/admin/users",
    "/admin/create_user",
    "/favorite_cat/999999",
    "/add_comment/999999",
    "/delete_comment/999999",
])
def test_removed_routes_are_unavailable(client, url):
    response = client.get(url)

    assert response.status_code == 404
