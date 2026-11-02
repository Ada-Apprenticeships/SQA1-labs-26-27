# Lab 4: Security assurance

**Aim:** demonstrate security flaws with tests, fix them, and use automated scanners, while understanding what the scanners miss.
**Time:** about 75 minutes.
**Assignment 1 criterion:** Security Assurance.

## 1. Run a static security scanner

```bash
git switch main && git pull
git switch -c fix/security
uv add --dev bandit
uv run bandit -r app
```

**Bandit** reads your Python code looking for risky patterns. It should report **B608: possible SQL injection** in `mine()` in `app/bookings.py`.

Bandit only flags *possible* problems. For each finding you must decide whether it is real (a **true positive**) or harmless (a **false positive**), and say why. That judgement is part of security assurance.

## 2. Prove the SQL injection (worked example)

`mine()` builds SQL by inserting the filter text `q` straight into a string:

```python
f"WHERE booking.user_id = {g.user.id} AND event.title LIKE '%{q}%'"
```

Create `tests/test_booking_security.py`. This test has bob make a booking, then has carol use a crafted filter to see it:

```python
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
```

Run `uv run pytest tests/test_booking_security.py`. It **fails**: carol can see bob's booking. The injected `OR 1=1` overrides the check on `user_id`, so the vulnerability is confirmed and it leaks other people's data. Commit the failing test.

## 3. Fix it

Never build SQL from user input. Use the ORM, which sends values separately from the query. Replace the body of `mine()` up to the `return` with:

```python
    q = request.args.get("q", "")
    bookings = db.session.scalars(
        db.select(Booking).join(Event)
        .where(Booking.user_id == g.user.id)
        .where(Event.title.contains(q, autoescape=True))
    ).all()
```

`autoescape=True` stops `%` and `_` in the filter acting as wildcards. Remove `from sqlalchemy import text`, which is no longer used. Run the tests and Bandit again: both should now be clean. Commit.

## 4. Prove and fix broken authorisation

Add this test to `tests/test_booking_security.py`:

```python
def test_user_cannot_cancel_someone_elses_booking(client, alice, bob, event):
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "1"})
    booking_id = Booking.query.one().id

    make_user("carol")
    login(client, "carol")
    response = client.post(f"/bookings/{booking_id}/cancel")

    assert response.status_code == 403
    assert Booking.query.count() == 1
```

It fails: carol can cancel bob's booking just by knowing its number. This kind of flaw is called an **insecure direct object reference**. Commit the failing test, then fix `cancel()` by checking ownership straight after loading the booking:

```python
    booking = db.get_or_404(Booking, booking_id)
    if booking.user_id != g.user.id:
        abort(403)
```

Add `abort` to the `from flask import ...` line. Run the tests and commit the fix.

Notice that **Bandit did not report this flaw**. Scanners find patterns in code; they cannot know your authorisation rules.

## 5. Check your dependencies

```bash
uv add --dev pip-audit
uv run pip-audit
```

**pip-audit** checks every installed package against a database of published vulnerabilities. It should report several for `urllib3 1.26.5`. Search the code: is `urllib3` actually used anywhere?

```bash
grep -r urllib3 app
```

An unused dependency with known vulnerabilities should be removed, not upgraded:

```bash
uv remove urllib3
uv run pip-audit
```

Also delete the `urllib3` line from `requirements.txt` so the pip route stays in step.

pip-audit **still** reports the old urllib3. Find out why:

```bash
uv tree --invert --package urllib3
```

Nothing in the app needs it any more, but `requests`, which pip-audit itself uses, does. uv kept the old version because it still satisfies that requirement. This is a **transitive dependency**: a package you never asked for directly. Upgrade it to a fixed version:

```bash
uv lock --upgrade-package urllib3
uv sync
uv run pip-audit
```

pip-audit should now report no known vulnerabilities. Commit `pyproject.toml`, `uv.lock` and `requirements.txt`.

## 6. Your turn

There is a **cross-site scripting (XSS)** flaw in this feature that Bandit cannot see, because it is in a template rather than in Python. Find it (look at your Lab 1 notes, and search the templates for `|safe`), then:

1. write a test that books with a note containing `<script>alert(1)</script>` and checks that the organiser's view of the event page does **not** contain it unescaped;
2. watch it fail, then fix the template;
3. open a pull request for all your security work and merge it.

## Checkpoint

Three security flaws are each demonstrated by a test that failed before the fix and passes after it. Bandit and pip-audit both run clean, and you can explain one thing each tool cannot detect.

## Apply it to Assignment 1

Run Bandit and pip-audit on your assignment repository and triage every finding: real or false positive, and why. Then look for the flaws the tools cannot see, especially authorisation and anything rendered with `|safe` or `Markup`. Demonstrate each one with a test before you fix it.

## Stretch

Read the OWASP Top 10:2025 entries for [A01 Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/) and [A05 Injection](https://owasp.org/Top10/2025/A05_2025-Injection/), and add the relevant category to your issue reports (for example, "A01:2025 Broken Access Control").