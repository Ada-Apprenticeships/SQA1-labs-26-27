"""Event bookings.

Draft generated with an AI coding assistant.
"""

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import login_required
from .booking_rules import booking_error
from .extensions import db
from .models import Booking, Event

bp = Blueprint("bookings", __name__)


@bp.route("/events/<int:event_id>/book", methods=["POST"])
@login_required
def book(event_id):
    event = db.get_or_404(Event, event_id)

    party_size = request.form.get("party_size", type=int)
    note = request.form.get("note", "")

    if party_size is None:
        error = "Please enter a number of places."
    else:
        error = booking_error(event.capacity, [b.party_size for b in event.bookings], party_size)
    if error:
        flash(error)
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
    bookings = db.session.scalars(
        db.select(Booking)
        .join(Event)
        .where(Booking.user_id == g.user.id)
        .where(Event.title.contains(q, autoescape=True))
    ).all()
    return render_template("my_bookings.html", bookings=bookings, q=q)


@bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.user_id != g.user.id:
        abort(403)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled.")
    return redirect(url_for("bookings.mine"))
