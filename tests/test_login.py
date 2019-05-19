import pytest
from flask import g, session
from app.db import get_db


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

def test_login_next(app, client, auth):
    response = client.get("/book")
    assert "next=%2Fbook%3F" in response.headers['Location']
    response = client.post("/login?next=/book",
        data = {
            "email": "user@user.com",
            "password": "a"
        }
    )
    assert response.headers['Location'] == "http://localhost/book"

    response = client.post("/login?next=http://corgiorgy.com",
        data = {
            "email": "user@user.com",
            "password": "a"
        }
    )
    assert response.headers['Location'] == "http://localhost/"
    

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

