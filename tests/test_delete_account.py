import pytest
from flask import url_for
from flask.testing import FlaskClient

from hushline.db import db
from hushline.model import (
    User,
)


@pytest.mark.usefixtures("_authenticated_user")
def test_delete_account(client: FlaskClient, user: User) -> None:
    # Make sure the user is there
    user_count = db.session.query(User).filter_by(id=user.id).count()
    assert user_count == 1

    # Delete the account
    response = client.post(url_for("settings.delete_account"))
    assert response.status_code == 302

    # Make sure the user is deleted
    user_count = db.session.query(User).filter_by(id=user.id).count()
    assert user_count == 0


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_cannot_delete_only_admin_account(client: FlaskClient, admin_user: User) -> None:
    # Make sure there is only one admin user
    admin_count = db.session.query(User).filter_by(is_admin=True).count()
    assert admin_count == 1

    # Make sure the user is there
    user_count = db.session.query(User).filter_by(id=admin_user.id).count()
    assert user_count == 1

    # Deleting the account should fail
    response = client.post(url_for("settings.delete_account"))
    assert response.status_code == 400

    # Make sure the user is still there
    user_count = db.session.query(User).filter_by(id=admin_user.id).count()
    assert user_count == 1


@pytest.mark.usefixtures("_authenticated_admin_user")
def test_delete_account_multiple_admins(
    client: FlaskClient, admin_user: User, admin_user2: User
) -> None:
    # Make sure there are two admin users
    admin_count = db.session.query(User).filter_by(is_admin=True).count()
    assert admin_count == 2

    # Make sure the user is there
    user_count = db.session.query(User).filter_by(id=admin_user.id).count()
    assert user_count == 1

    # Deleting the account should work
    response = client.post(url_for("settings.delete_account"))
    assert response.status_code == 302

    # Make sure the user is deleted
    user_count = db.session.query(User).filter_by(id=admin_user.id).count()
    assert user_count == 0
