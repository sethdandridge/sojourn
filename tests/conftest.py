import os
import tempfile

import pytest
from fortnite import create_app
from fortnite.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():

    app = create_app({"TESTING": True, "DATABASE": "dbname=fortnite_test"})

    with app.app_context():
        init_db()
        with get_db().cursor() as cursor:
            cursor.execute(_data_sql)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="user@user.com", password="a"):
        return self._client.post("/login", data={"email": email, "password": password})

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
