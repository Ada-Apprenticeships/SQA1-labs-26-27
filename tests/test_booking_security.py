from app.models import Booking
from conftest import login, make_user


def test_bookings_filter_is_not_vulnerable_to_sql_injection(client, alice, bob, event):
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "1"})

    make_user("carol")
    login(client, "carol")
    response = client.get("/bookings", query_string={"q": "x' OR 1=1 OR event.title LIKE '"})

    assert response.status_code == 200
    assert b"Pytest Workshop" not in response.data


def test_user_cannot_cancel_someone_elses_booking(client, alice, bob, event):
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "1"})
    booking_id = Booking.query.one().id

    make_user("carol")
    login(client, "carol")
    response = client.post(f"/bookings/{booking_id}/cancel")

    assert response.status_code == 403
    assert Booking.query.count() == 1