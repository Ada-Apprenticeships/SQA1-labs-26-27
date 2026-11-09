"""Booking rules, kept separate from Flask so they are easy to test."""

MAX_PARTY = 4


def places_remaining(capacity, party_sizes):
    """Return how many places are left, given the party size of each booking."""
    return capacity - sum(party_sizes)


def booking_error(capacity, party_sizes, party_size, max_party=MAX_PARTY):
    """Return an error message if a booking is not allowed, otherwise None."""
    if party_size < 1:
        return "Please book at least one place."
    if party_size > max_party:
        return f"You can book at most {max_party} places."
    if party_size > places_remaining(capacity, party_sizes):
        return "Sorry, there are not enough places left."
    return None
