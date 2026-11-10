"""Command-line helpers: flask --app run init-db / seed."""

from datetime import timedelta

import click

from .extensions import db
from .models import Event, User, utcnow


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Drop and recreate all tables."""
        db.drop_all()
        db.create_all()
        click.echo("Initialised the database.")

    @app.cli.command("seed")
    def seed():
        """Create three users and six events."""
        users = {}
        for name in ("alice", "bob", "carol"):
            user = User(username=name)
            user.set_password("password123")
            db.session.add(user)
            users[name] = user
        now = utcnow()
        samples = [
            ("Intro to Pytest", "Hands-on session on testing Flask apps.", "Room 1", 3, 20),
            ("Secure Coding Clinic", "Bring your code; we review it together.", "Room 2", 5, 12),
            ("Accessibility Walkthrough", "Testing a site with a screen reader.", "Online", 7, 30),
            ("CI Pipelines Q&A", "Questions on GitHub Actions.", "Room 1", 10, 4),
            ("Code Review Dojo", "Practise reviewing pull requests.", "Room 3", 14, 8),
            ("Last Month's Retro", "This event has already happened.", "Room 1", -30, 10),
        ]
        for title, desc, location, days, capacity in samples:
            db.session.add(
                Event(
                    title=title,
                    description=desc,
                    location=location,
                    starts_at=now + timedelta(days=days),
                    capacity=capacity,
                    organiser=users["alice"],
                )
            )
        db.session.commit()
        click.echo("Seeded 3 users (alice, bob, carol; password: password123) and 6 events.")
