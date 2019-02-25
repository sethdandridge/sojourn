import pytest
from flask import g, session
from fortnite.db import get_db


def test_login(app, client, auth):
    assert client.get("/login").status_code == 200
    response = auth.login()
    assert "http://localhost/" == response.headers["Location"]

    with client:
        client.get("/")
        assert session["user_id"] == 2
        assert g.user["email"] == "user@user.com"

    with client:
        with client.session_transaction() as sess:
            sess['user_id'] = 20
        client.get("/")
        assert session.get('user_id') is None

@pytest.mark.parametrize(
    ("email", "password", "message"),
    (
        ("asdf@asdf.com", "pw1234", b"Incorrect username."),
        ("user@user.com", "69", b"Incorrect password."),
    ),
)
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


def test_login_required(client, auth):
    response = client.get("/")
    # if no login cookie found, send to login page
    assert "http://localhost/login/" == response.headers["Location"]

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
