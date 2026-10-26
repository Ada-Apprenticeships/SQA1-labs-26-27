"""Event listing and detail pages."""
from flask import Blueprint, render_template

from .extensions import db
from .models import Event, utcnow

bp = Blueprint("events", __name__)


@bp.route("/")
def index():
    events = db.session.scalars(
        db.select(Event).where(Event.starts_at >= utcnow()).order_by(Event.starts_at)
    ).all()
    return render_template("index.html", events=events)


@bp.route("/events/<int:event_id>")
def view(event_id):
    event = db.get_or_404(Event, event_id)
    return render_template("event.html", event=event)
