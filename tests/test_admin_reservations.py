import pytest
from flask import g, session
from app.db import get_db


def test_admin_reservations(app, auth, client):
    with app.app_context() as app:
        with get_db().cursor() as cursor:
            cursor.execute(
                "INSERT INTO reservation "
                " (user_id, property_id, status_id, arrival, departure, name) "
                " VALUES "
                " (2, 1, 2, '2030-01-01', '2030-01-02', 'Mishkas birthday');"
            )

    auth.login(email="admin@admin.com")
    response = client.get("/admin/reservations/edit/12345")
    assert response.status_code == 404

    auth.login(email="admin@admin.com")
    assert client.get("/admin/reservations/edit/1").status_code == 200

    response = client.post("/admin/reservations/edit/1",
        data={
            "status": "1"
        },
        follow_redirects=True
    )
    assert b"Mishkas" in response.data

    response = client.post("/admin/reservations/edit/1",
        data={
            "status": "2 23 2"
        },
        follow_redirects=True
    )
    assert b"Invalid status. What are you doing?" in response.data
