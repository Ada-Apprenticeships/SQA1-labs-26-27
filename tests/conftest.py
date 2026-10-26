from datetime import timedelta

import pytest

from app import create_app
from app.extensions import db
from app.models import Event, User, utcnow


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(name):
    user = User(username=name)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def alice(app):
    return make_user("alice")


@pytest.fixture
def bob(app):
    return make_user("bob")


@pytest.fixture
def event(alice):
    e = Event(title="Pytest Workshop", description="Testing Flask apps", location="Room 1",
              starts_at=utcnow() + timedelta(days=7), capacity=5, organiser=alice)
    db.session.add(e)
    db.session.commit()
    return e


def login(client, username):
    return client.post("/auth/login", data={"username": username, "password": "password123"})
