import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient

from hushline.db import db
from hushline.model import (
    User,
)


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_admin_settings_shows_verified_on_managed_service(
    app: Flask, client: FlaskClient, user: User
) -> None:
    app.config["USER_VERIFICATION_ENABLED"] = True

    response = client.get(url_for("settings.admin"), follow_redirects=True)
    assert response.status_code == 200
    assert "Toggle Verified" in response.text


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_admin_settings_hides_verified_on_nonmanaged_service(
    app: Flask, client: FlaskClient, user: User
) -> None:
    app.config["USER_VERIFICATION_ENABLED"] = False

    response = client.get(url_for("settings.admin"), follow_redirects=True)
    assert response.status_code == 200
    assert "Toggle Verified" not in response.text


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_toggle_verified_on_managed_service(
    app: Flask, client: FlaskClient, admin_user: User
) -> None:
    app.config["USER_VERIFICATION_ENABLED"] = True

    response = client.post(
        url_for("admin.toggle_verified", user_id=admin_user.id),
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_toggle_verified_on_nonmanaged_service(
    app: Flask, client: FlaskClient, admin_user: User
) -> None:
    app.config["USER_VERIFICATION_ENABLED"] = False

    response = client.post(
        url_for("admin.toggle_verified", user_id=admin_user.id),
        follow_redirects=True,
    )
    assert response.status_code == 401


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_toggle_admin_only_admin(client: FlaskClient, admin_user: User) -> None:
    # Make sure there is only one admin user
    admin_count = db.session.query(User).filter_by(is_admin=True).count()
    assert admin_count == 1

    # Make sure the user is an admin
    assert admin_user.is_admin is True

    # Toggling admin on the user should return 400
    response = client.post(
        url_for("admin.toggle_admin", user_id=admin_user.id),
        follow_redirects=True,
    )
    assert response.status_code == 400


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_toggle_admin_multiple_admins(
    client: FlaskClient, admin_user: User, admin_user2: User
) -> None:
    assert admin_user.is_admin is True
    assert admin_user2.is_admin is True

    # Make sure there are two admin users
    admin_count = db.session.query(User).filter_by(is_admin=True).count()
    assert admin_count == 2

    # Toggling admin on the user should return 302 (successfully redirect)
    response = client.post(url_for("admin.toggle_admin", user_id=admin_user.id))
    assert response.status_code == 302

    # There should be only one admins now
    admin_count = db.session.query(User).filter_by(is_admin=True).count()
    assert admin_count == 1
