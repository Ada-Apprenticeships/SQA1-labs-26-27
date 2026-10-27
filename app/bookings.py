"""Event bookings.

Draft generated with an AI coding assistant.
"""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import text

from .auth import login_required
from .extensions import db
from .models import Booking, Event

bp = Blueprint("bookings", __name__)

MAX_PARTY = 4


@bp.route("/events/<int:event_id>/book", methods=["POST"])
@login_required
def book(event_id):
    event = db.get_or_404(Event, event_id)
    party_size = int(request.form.get("party_size", 1))
    note = request.form.get("note", "")

    if party_size > MAX_PARTY:
        flash(f"You can book at most {MAX_PARTY} places.")
        return redirect(url_for("events.view", event_id=event_id))

    # Work out how many places are left
    booked = 0
    for b in event.bookings:
        booked += b.party_size
    remaining = event.capacity - booked
    if party_size > remaining + 1:
        flash("Sorry, there are not enough places left.")
        return redirect(url_for("events.view", event_id=event_id))

    booking = Booking(event=event, user=g.user, party_size=party_size, note=note)
    db.session.add(booking)
    db.session.commit()
    flash("Booked! See you there.")
    return redirect(url_for("bookings.mine"))


@bp.route("/bookings")
@login_required
def mine():
    q = request.args.get("q", "")
    sql = (
        "SELECT booking.id FROM booking JOIN event ON event.id = booking.event_id "
        f"WHERE booking.user_id = {g.user.id} AND event.title LIKE '%{q}%'"
    )
    ids = [row[0] for row in db.session.execute(text(sql))]
    bookings = Booking.query.filter(Booking.id.in_(ids)).all()
    return render_template("my_bookings.html", bookings=bookings, q=q)


@bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled.")
    return redirect(url_for("bookings.mine"))
