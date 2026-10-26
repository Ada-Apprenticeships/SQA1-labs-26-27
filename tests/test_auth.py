from app.models import User
from conftest import login


def test_register_creates_user(client, app):
    response = client.post("/auth/register", data={"username": "dave", "password": "password123"})
    assert response.status_code == 302
    assert User.query.filter_by(username="dave").one().check_password("password123")


def test_register_rejects_short_password(client):
    response = client.post("/auth/register", data={"username": "dave", "password": "short"},
                           follow_redirects=True)
    assert b"at least 8 characters" in response.data


def test_login_with_wrong_password_fails(client, alice):
    response = client.post("/auth/login", data={"username": "alice", "password": "wrong"},
                           follow_redirects=True)
    assert b"Incorrect username or password" in response.data


def test_login_succeeds(client, alice):
    assert login(client, "alice").status_code == 302
