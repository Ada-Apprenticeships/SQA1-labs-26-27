from app.booking_rules import booking_error, places_remaining


def test_places_remaining():
    # Capacity 10, with bookings of 2 and 3 places: 5 should be left
    assert places_remaining(10, [2, 3]) == 5


def test_valid_booking_has_no_error():
    # Capacity 10, no bookings yet: booking 2 places should be allowed (no error)
    assert booking_error(10, [], 2) is None


def test_full_event_is_rejected():
    # Capacity 5, already full with one booking of 5: booking 1 more should be rejected
    assert booking_error(5, [5], 1) is not None


def test_party_size_of_one_is_allowed():
    assert booking_error(10, [], 1) is None