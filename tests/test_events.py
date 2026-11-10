from datetime import timedelta

from conftest import login

from app.extensions import db
from app.models import Event, utcnow


def test_index_lists_upcoming_events(client, event):
    assert b"Pytest Workshop" in client.get("/").data


def test_index_hides_past_events(client, alice):
    db.session.add(
        Event(
            title="Old Event",
            description="x",
            location="y",
            starts_at=utcnow() - timedelta(days=1),
            capacity=5,
            organiser=alice,
        )
    )
    db.session.commit()
    assert b"Old Event" not in client.get("/").data


def test_event_page_shows_details(client, event):
    response = client.get(f"/events/{event.id}")
    assert b"Room 1" in response.data


def test_places_left_counts_places_not_bookings(client, alice, bob, event):
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "4"})
    response = client.get(f"/events/{event.id}")
    assert b"Places left: 1 of 5" in response.data
