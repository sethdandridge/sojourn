import pytest
from flask import g, session
from fortnite.db import get_db

def test_admin_required(auth, client):
    with client:
        auth.login()
        response = client.get("/admin/guests")
        assert response.status_code == 401

    with client:
        auth.login(email="admin@admin.com")
        response = client.get("admin/guests")
        assert response.status_code == 200
