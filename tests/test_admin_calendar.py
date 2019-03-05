import pytest
from flask import g, session
from app.db import get_db


def test_admin_calendar(auth, client):
    auth.login(email="admin@admin.com")
    assert client.get("/admin/calendar").status_code == 200

    # so lazy... this is not a unit test
    assert client.get("/admin/calendar?show_past=true&show_canceled_and_denied=true").status_code == 200
