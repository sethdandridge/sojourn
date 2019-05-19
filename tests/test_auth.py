import pytest
from flask import g, session
from app.db import get_db

def test_login_required(client, auth):
    response = client.get("/")
    # if no login cookie found, send to login page
    assert "http://localhost/login" == response.headers["Location"]

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data

def test_emaiL_confirmation_required(app, client, auth):
    auth.login("uncomfirmed@uncomfirmed.com")
    response = client.get("/create_property")
    assert b"You must confirm your email" in response.data
