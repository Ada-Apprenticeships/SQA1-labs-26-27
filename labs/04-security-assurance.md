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

Run `uv run pytest tests/test_booking_security.py`. It **fails**: carol can see bob's booking. The injected `OR 1=1` overrides the check on `user_id`, so the vulnerability is confirmed and it leaks other people's data.

The test describes the **secure** behaviour, so it fails now and will pass once the code is fixed. That is the same test-first pattern as Lab 2.

Commit the failing test on its own, before you change any app code, so your history shows the vulnerability was proved before it was fixed:

```bash
git add tests/test_booking_security.py
git commit -m "Add failing test for SQL injection in bookings filter (#N)"
```

Replace `N` with the number of the issue for this defect. If you did not log one in Lab 1, create it now (**Issues → New issue → Defect report**), with severity **High** and the ISO/IEC 25010 characteristic **Security**, then use its number.

## 3. Fix it

Never build SQL from user input. Use the ORM, which sends values separately from the query.

In `app/bookings.py`:

1. Replace the **whole** `mine()` function, from `@bp.route("/bookings")` down to its `return`, with this version:

```python
@bp.route("/bookings")
@login_required
def mine():
    q = request.args.get("q", "")
    bookings = db.session.scalars(
        db.select(Booking).join(Event)
        .where(Booking.user_id == g.user.id)
        .where(Event.title.contains(q, autoescape=True))
    ).all()
    return render_template("my_bookings.html", bookings=bookings, q=q)
```

2. Delete the line `from sqlalchemy import text` near the top. Nothing uses it now.

The old version pasted `q` into the SQL text. This one passes it to the database as a value, so whatever the user types is only ever treated as text to search for, never as part of the query. `autoescape=True` stops `%` and `_` in the filter acting as wildcards.

Run the tests and Bandit again: both should now be clean. Commit the fix, using the same issue number:

```bash
git add app/bookings.py
git commit -m "Use the ORM for the bookings filter (fixes #N)"
```

## 4. Prove and fix broken authorisation

Requirement R5 says users can cancel **their own** bookings only, but `cancel()` deletes whichever booking id it is given.

**Prove it.** Add this test to the end of `tests/test_booking_security.py`. Bob makes a booking, the test looks up its id, then carol tries to cancel it. The test expects a **403 Forbidden** response, and bob's booking still to be there:

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

Run `uv run pytest tests/test_booking_security.py`. The new test **fails**: carol can cancel bob's booking just by knowing its number. This kind of flaw is called an **insecure direct object reference**.

Commit the failing test on its own, as before:

```bash
git add tests/test_booking_security.py
git commit -m "Add failing test for cancelling another user's booking (#N)"
```

Replace `N` with the number of the issue for this defect. You may not have logged one in Lab 1, because it is hard to see from the browser: if not, create it now, with severity **High**, characteristic **Security** and requirement **R5**.

**Fix it.** In `app/bookings.py`:

1. Add `abort` to the Flask import at the top, so it reads:

```python
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
```

2. Replace the **whole** `cancel()` function, from `@bp.route("/bookings/<int:booking_id>/cancel", ...)` down to its `return`, with this version. The only change is the two lines that check who owns the booking:

```python
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
```

Run `uv run pytest`: every test should now pass. Commit the fix:

```bash
git add app/bookings.py
git commit -m "Only let users cancel their own bookings (fixes #N)"
```

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

pip-audit should now report **No known vulnerabilities found**. If it still lists urllib3, check you ran `uv sync` after the upgrade.

Then commit the dependency changes:

1. Run `git status`. You should see changes to `pyproject.toml` (urllib3 removed, Bandit and pip-audit added), `uv.lock` (the locked versions) and `requirements.txt`. Your test and app changes should already be committed from sections 2 to 4.
2. Commit the three files together, so the change to the dependencies is one step in your history:

```bash
git add pyproject.toml uv.lock requirements.txt
git commit -m "Remove unused urllib3 and upgrade the transitive copy; add security tools"
```

If you logged an issue for the vulnerable dependency, add `(fixes #N)` to the message.

## 6. Your turn

There is a **cross-site scripting (XSS)** flaw in this feature that Bandit cannot see, because it is in a template rather than in Python. Find it (look at your Lab 1 notes, and search the templates for `|safe`), then:

1. write a test that books with a note containing `<script>alert(1)</script>` and checks that the organiser's view of the event page does **not** contain it unescaped;
2. watch it fail, then fix the template;
3. open a pull request for all your security work and merge it.

Stuck, or short of time? The [Lab 4 hints and tips](https://staticwebsitesjr.z33.web.core.windows.net/sqa1/sqa1-lab4-hints.html) take you through it one hint at a time.

## Checkpoint

Three security flaws are each demonstrated by a test that failed before the fix and passes after it. Bandit and pip-audit both run clean, and you can explain one thing each tool cannot detect.

## Apply it to Assignment 1

Run Bandit and pip-audit on your assignment repository and triage every finding: real or false positive, and why. Then look for the flaws the tools cannot see, especially authorisation and anything rendered with `|safe` or `Markup`. Demonstrate each one with a test before you fix it.

## Stretch

Read the OWASP Top 10:2025 entries for [A01 Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/) and [A05 Injection](https://owasp.org/Top10/2025/A05_2025-Injection/), and add the relevant category to your issue reports (for example, "A01:2025 Broken Access Control").

## Extension: Dependabot (optional, about 15 minutes)

pip-audit only checks your dependencies when you run it. **Dependabot**, built into GitHub, watches them all the time.

### 1. Turn on alerts and security updates

On GitHub, open your labs repository and go to **Settings → Advanced Security**. Under **Dependabot**, click **Enable** for **Dependabot alerts** and **Dependabot security updates**.

- **Alerts** appear under the **Security** tab when a dependency has a published vulnerability.
- **Security updates** are pull requests that Dependabot opens to upgrade a vulnerable package for you.

### 2. Keep everything up to date

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
```

Commit and push it. Dependabot reads `uv.lock` and opens a pull request for each package with a newer version. These are **version updates**: not every one fixes a vulnerability, but staying current makes the security fixes easier to take when they come.

Look at the **Insights → Dependency graph → Dependabot** page to check it ran, then look at any pull requests it has opened.

### 3. Think about it

- Should you merge a Dependabot pull request straight away? What could an upgrade break, and what tells you it did not? (After Thursday's lab, your CI pipeline runs the tests on every one.)
- Name one thing Dependabot cannot find that your Lab 4 security tests can.

### Apply it to Assignment 1

Turn on Dependabot alerts in your assignment repository too. Triage anything it reports the same way as a pip-audit finding, and mention it in your video if it is part of how you keep your feature secure.