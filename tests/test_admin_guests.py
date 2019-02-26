import pytest
from flask import g, session
from fortnite.db import get_db


def test_admin_guests_edit(auth, client):
    auth.login(email="admin@admin.com")
    response = client.get("/admin/guests/edit/2")
    assert response.status_code == 200

    response = client.get("/admin/guests/edit/1000000", follow_redirects=True)
    assert b"This guest does not exist." in response.data

    response = client.post(
        f"/admin/guests/edit/2",
        data={"is_admin": "1", "note": "This is now the note."},
        follow_redirects=True,
    )
    assert b"user user (Admin)" in response.data
    assert b"This is now the note." in response.data


@pytest.mark.parametrize(
    ("guest_id", "is_admin", "note", "message"),
    (
        (10000, None, None, b"This guest does not exist."),
        (1, None, None, b"You cannot edit yourself."),
        (2, "1", "X" * 256, b"Note exceeds maximum length (255 characters)."),
    ),
)
def test_admin_guests_edit_validate_input(
    auth, client, guest_id, is_admin, note, message
):
    auth.login(email="admin@admin.com")
    response = client.post(
        f"/admin/guests/edit/{guest_id}",
        data={"is_admin": is_admin, "note": note},
        follow_redirects=True,
    )
    print(response.data)
    assert message in response.data


def test_admin_guests_remove(auth, client):
    auth.login(email="admin@admin.com")
    response = client.get("/admin/guests/remove/2")
    assert response.status_code == 200

    response = client.post("/admin/guests/remove/1", follow_redirects=True)
    assert b"HEY! You are not allowed to remove the property owner." in response.data

    response = client.post("/admin/guests/remove/2", follow_redirects=True)
    assert b"test test" not in response.data


def test_admin_guests_remove_onseself(app, auth, client):
    # make user 2 an admin
    with app.app_context() as app:
        sql = "UPDATE user_to_property SET is_admin=TRUE WHERE user_id = 2 AND property_id = 1;"
        with get_db().cursor() as cursor:
            cursor.execute(sql)

    with client:
        auth.login()
        client.get("/switch_property/1")
        client.get("/admin/guests/remove/2")
        response = client.post("/admin/guests/remove/2", follow_redirects=True)
        assert b"Welcome home" in response.data


def test_admin_invite_guest(app, auth, client):
    auth.login(email="admin@admin.com")
    assert client.get("/admin/guests/invite").status_code == 200

    response = client.post(
        "/admin/guests/invite", data={"email": "notguest@notguest.com"}
    )
    response = client.get("/admin/guests")
    assert b"notguest" in response.data

    response = client.post(
        "/admin/guests/invite", data={"email": "newuser@newuser.com"}
    )

    response = client.get("/admin/guests/invites")
    assert b"newuser" in response.data


@pytest.mark.parametrize(
    (
        "email",
        "max_upcoming",
        "max_duration",
        "max_per_month",
        "max_per_year",
        "max_days_in_advance",
        "min_days_between",
        "is_owner_presence_required",
        "is_owner_confirmation_required",
        "message",
    ),
    (
        (
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            b"Please enter the email address of the guest you wish to invite.",
        ),
        (
            "user@user.com",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            b"User is already a guest at this property.",
        ),
        (
            "invited@invited.com",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            b"Invite has already been sent to this user.",
        ),
        (
            "newuser@newuser.com",
            "a",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            b"Invalid Max Upcoming Stays. Please enter a reasonable number of stays.",
        ),
        (
            "newuser@newuser.com",
            "",
            "-1",
            "",
            "",
            "",
            "",
            "",
            "",
            b"Invalid Max Stay Duration. Please enter a reasonable number of days.",
        ),
        (
            "newuser@newuser.com",
            "",
            "",
            "2147483648",
            "",
            "",
            "",
            "",
            "",
            b"Invalid Max Stays Per Month. Please enter a reasonable number of stays.",
        ),
        (
            "newuser@newuser.com",
            "",
            "",
            "",
            "asdf",
            "",
            "",
            "",
            "",
            b"Invalid Max Stays Per Year. Please enter a reasonable number of stays.",
        ),
        (
            "newuser@newuser.com",
            "",
            "",
            "",
            "",
            "12312b2121",
            "",
            "",
            "",
            b"Invalid Max Days In Advance. Please enter a reasonable number of days.",
        ),
        (
            "newuser@newuser.com",
            "",
            "",
            "",
            "",
            "",
            "2.5",
            "",
            "",
            b"Invalid Minimum Nights Between Stays. Please enter a reasonable number of days.",
        ),

    ),
)
def test_admin_invite_guest_input_validation(
    app,
    auth,
    client,
    email,
    max_upcoming,
    max_duration,
    max_per_month,
    max_per_year,
    max_days_in_advance,
    min_days_between,
    is_owner_presence_required,
    is_owner_confirmation_required,
    message,
):
    auth.login(email='admin@admin.com')
    response = client.post("/admin/guests/invite",
        data={
            "email": email,
            "max_upcoming": max_upcoming,
            "max_duration": max_duration,
            "max_per_month": max_per_month,
            "max_per_year": max_per_year,
            "max_days_in_advance": max_days_in_advance,
            "min_days_between": min_days_between,
            "is_owner_presence_required": is_owner_presence_required,
            "is_owner_confirmation_required": is_owner_confirmation_required,
        }
    )
    assert message in response.data

def test_admin_edit_invite(app, auth, client):
    auth.login(email="admin@admin.com")
    assert client.get('/admin/guests/invites/edit/1').status_code == 200

    response = client.post('/admin/guests/invites/edit/1',
        data={
            "max_upcoming": 1234,
        }
    )
    assert response.status_code == 302
    response = client.get('/admin/guests/invites/edit/1') 
    assert b"1234" in response.data

    response = client.post('/admin/guests/invites/edit/10000')
    assert response.status_code == 401

    response = client.post('/admin/guests/invites/edit/1',
        data={
            "max_upcoming": -1,
        }
    )
    assert b"Invalid Max Upcoming Stays. Please enter a reasonable number of stays." in response.data

    response = client.get('/admin/guests/invites/edit/123123')
    assert response.status_code == 401

def test_admin_remove_invite(app, auth, client):
    auth.login(email="admin@admin.com")

    assert client.get("/admin/guests/invites/remove/1").status_code == 200

    assert client.get("/admin/guests/invites/remove/123123123").status_code == 401

    client.post("/admin/guests/invites/remove/1")
    assert b"invited@invited.com" not in client.get("/admin/guests/invites").data

    response = client.post('admin/guests/invites/remove/100000')
    assert response.status_code == 401
