# Tests generated with an AI coding assistant.
from app.models import Booking
from conftest import login


def test_book_event(client, alice, event):
    login(client, "alice")
    response = client.post(f"/events/{event.id}/book", data={"party_size": "2"})
    assert response.status_code == 302


def test_booking_saved(client, alice, event):
    login(client, "alice")
    client.post(f"/events/{event.id}/book", data={"party_size": "1"})
    assert Booking.query.count() == 1


def test_my_bookings_page_loads(client, alice):
    login(client, "alice")
    assert client.get("/bookings").status_code == 200


def test_cancel_booking(client, alice, event):
    login(client, "alice")
    client.post(f"/events/{event.id}/book", data={"party_size": "1"})
    booking = Booking.query.first()
    response = client.post(f"/bookings/{booking.id}/cancel")
    assert response.status_code == 302
