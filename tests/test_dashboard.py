import pytest
from flask import g, session
from fortnite.db import get_db
import datetime

def test_book(app, client, auth):
    auth.login()
    assert client.get('/book').status_code == 200

    arrival = datetime.date.today() + datetime.timedelta(days=1)
    departure = datetime.date.today() + datetime.timedelta(days=5)
    arrival = arrival.strftime("%Y-%m-%d")
    departure = departure.strftime("%Y-%m-%d")

    response = client.post(
        "/book",
        data={
            "arrival_date": arrival,
            "departure_date": departure,
            "name": "Mishka's Birthday"
        },
    ) 
    assert "/book/success" in response.headers["Location"]

    with app.app_context():
        assert (
            get_db().execute("select * from reservation").fetchone()
            is not None
        )

    from fortnite.dashboard import get_booked_dates
    booked_night = datetime.date.today() + datetime.timedelta(days=2)
    with app.app_context():
        booked_dates = get_booked_dates(get_db())
        print(booked_dates)
        assert f"{booked_night.year}, {booked_night.month - 1}, {booked_night.day}" in booked_dates


arrival = datetime.date.today() + datetime.timedelta(days=6)
departure = datetime.date.today() + datetime.timedelta(days=10)
arrival = arrival.strftime("%Y-%m-%d")
departure = departure.strftime("%Y-%m-%d")
@pytest.mark.parametrize(
    ("arrival", "departure", "name", "message"),
    (
        ("", departure, "", b"Please specify an arrival date."),
        (arrival, "", "", b"Please specify a departure date."),
    ),
)
def test_book_validate_input(client, auth, arrival, departure, name, message):
    auth.login()
    response = client.post(
        "/book",
        data={
            "arrival_date": arrival,
            "departure_date": departure,
            "name": name,
        },
    )
    assert message in response.data

def test_reservations(app, auth, client):
    auth.login()

    arrival = datetime.date.today() + datetime.timedelta(days=1)
    departure = datetime.date.today() + datetime.timedelta(days=5)
    arrival = arrival.strftime("%Y-%m-%d")
    departure = departure.strftime("%Y-%m-%d")

    arrival_2 = datetime.date.today() + datetime.timedelta(days=6)
    departure_2 = datetime.date.today() + datetime.timedelta(days=10)
    arrival_2 = arrival_2.strftime("%Y-%m-%d")
    departure_2 = departure_2.strftime("%Y-%m-%d")

    response = client.post(
        "/book",
        data={
            "arrival_date": arrival,
            "departure_date": departure,
            "name": "Mishka's Birthday"
        },
    )

    response = client.post(
        "/book",
        data={
            "arrival_date": arrival_2,
            "departure_date": departure_2, 
        },
    )

    response = client.get('/reservations')
    assert b"Mishka's Birthday" in response.data

    
