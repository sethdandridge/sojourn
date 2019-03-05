import pytest
from flask import g, session
from app.db import get_db


def test_register(client, app):
    assert client.get("/register").status_code == 200
    response = client.post(
        "/register",
        data={
            "email": "test2",
            "password": "test2",
            "first_name": "test2",
            "last_name": "test2",
        },
    )
    assert "http://localhost/" == response.headers["Location"]

    with app.app_context():
        sql = (
            "select * from \"user\" where email LIKE 'test2'"
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql)
            user = cursor.fetchone()
        assert user is not None


@pytest.mark.parametrize(
    ("email", "password", "first_name", "last_name", "message"),
    (
        ("", "password", "first_name", "last_name", b"Email is required."),
        ("email", "", "first_name", "last_name", b"Password is required."),
        ("email", "password", "", "last_name", b"First name is required."),
        ("email", "password", "first_name", "", b"Last name is required."),
        (
            "user@user.com",
            "password",
            "first_name",
            "last_name",
            b"is already registered",
        ),
    ),
)
def test_register_validate_input(
    client, email, password, first_name, last_name, message
):
    response = client.post(
        "/register",
        data={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert message in response.data
