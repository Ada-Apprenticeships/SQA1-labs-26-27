# Tests generated with an AI coding assistant.
from app.models import Booking
from conftest import login, make_user
import pytest


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


@pytest.mark.parametrize("second_party, expected_total", [
    (1, 5),  # carol books 1: 4 + 1 = 5 fills the event, so allowed
    (2, 4),  # carol books 2: 4 + 2 = 6 is too many, so rejected; total stays at 4
])
def test_bookings_cannot_exceed_capacity(client, alice, bob, event, second_party, expected_total):
    # event fixture has capacity 5: bob takes 4 places, then carol tries to book
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "4"})
    make_user("carol")
    login(client, "carol")
    client.post(f"/events/{event.id}/book", data={"party_size": str(second_party)})
    assert sum(b.party_size for b in Booking.query.all()) == expected_total