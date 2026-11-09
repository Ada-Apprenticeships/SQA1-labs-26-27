# Lab 3: Coverage, mutation testing and testable design

**Aim:** measure how good your tests really are, and restructure code so its rules can be tested properly.
**Time:** about 90 minutes.
**Assignment 1 criteria:** Testing; Code Quality and Measurement.

## 1. Measure coverage

Start a branch and add the coverage plugin as a development dependency:

```bash
git switch main && git pull
git switch -c test/effectiveness
uv add --dev pytest-cov
uv run pytest --cov=app --cov-report=term-missing
```

Look at the line for `app/bookings.py`. Coverage is already **above 90%**, even though you found several defects in Lab 1.

> **Coverage tells you which lines ran, not whether your tests would notice if they were wrong.** High coverage with weak assertions is common, especially with AI-generated tests.

The `Missing` column is still useful: it shows code no test touches at all.

## 2. Make the rules testable

Mutation testing (next step) changes your code in small ways and checks whether your tests notice. The tool used here, **mutmut**, does not mutate functions that have decorators, so it cannot test the rules buried inside the `book()` route. That is a design problem as well as a tooling one: business rules mixed into web handlers are hard to test.

The fix is a classic refactoring: **extract the rules into plain functions.** Create `app/booking_rules.py`:

```python
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
```

Now use it in `app/bookings.py`:

1. Add `from .booking_rules import booking_error` to the imports, and delete the line `MAX_PARTY = 4`.
2. Replace the **whole** `book()` function, from `@bp.route(...)` down to its final `return`, with this version:

```python
@bp.route("/events/<int:event_id>/book", methods=["POST"])
@login_required
def book(event_id):
    event = db.get_or_404(Event, event_id)
    party_size = request.form.get("party_size", type=int)
    note = request.form.get("note", "")

    if party_size is None:
        error = "Please enter a number of places."
    else:
        error = booking_error(event.capacity,
                              [b.party_size for b in event.bookings], party_size)
    if error:
        flash(error)
        return redirect(url_for("events.view", event_id=event_id))

    # Any checks you added for R3 or R4 in Lab 2 go here

    booking = Booking(event=event, user=g.user, party_size=party_size, note=note)
    db.session.add(booking)
    db.session.commit()
    flash("Booked! See you there.")
    return redirect(url_for("bookings.mine"))
```

If you added checks for R3 or R4 in Lab 2, copy them from your old version into the marked place before you delete it.

`type=int` returns `None` instead of crashing when the input is not a number, and `booking_error` now rejects zero and negative party sizes. Run `uv run pytest` to check nothing broke.

## 3. Add some quick tests

Create `tests/test_booking_rules.py` with these deliberately thin tests, the kind an AI assistant often produces:

```python
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
```

Each call passes the event's capacity, a list of the party sizes already booked, and (for `booking_error`) the party size being requested. `booking_error` returns `None` if the booking is allowed, or an error message if not.

They pass, and they cover most of `booking_rules.py`. Are they good enough?

## 4. Run mutation testing

Add mutmut and tell it what to mutate and which tests to run. Add this to the end of `pyproject.toml`:

```toml
[tool.mutmut]
source_paths = ["app/"]
only_mutate = ["app/booking_rules.py"]
pytest_add_cli_args_test_selection = ["tests/test_booking_rules.py"]
```

Then:

```bash
uv add --dev mutmut
uv run mutmut run
uv run mutmut results
```

mutmut creates **mutants**: copies of your code with one small change, such as `<` turned into `<=`. If a test fails, the mutant is **killed** (good). If every test still passes, it **survived**: your tests cannot tell the difference between the real code and the broken version.

With the thin tests, most mutants survive. Look at one:

```bash
uv run mutmut show app.booking_rules.x_booking_error__mutmut_1
```

You should see `party_size < 1` changed to `party_size <= 1`. That would wrongly reject a booking for one person, yet no test noticed.

## 5. Kill the mutant (worked example)

Add a test at the boundary the mutant changed:

```python
def test_party_size_of_one_is_allowed():
    assert booking_error(10, [], 1) is None
```

mutmut saves its results in the `mutants/` folder and only retests a mutant when the app code changes, not when your tests do. So delete the folder before each new run:

```bash
rm -rf mutants
uv run mutmut run
uv run mutmut results
```

Mutant 1 is no longer listed: your new test killed it.

## 6. Your turn

Add tests until **every mutant is killed**. Use `mutmut results` and `mutmut show` to see what each survivor changed, then ask what test would notice. Remember `rm -rf mutants` before each `uv run mutmut run`. Stuck? Try the [Lab 3 hint sheet](https://staticwebsitesjr.z33.web.core.windows.net/sqa1/sqa1-lab3-hints.html), one hint at a time. Hints:

- test both sides of every boundary (zero and one; the maximum and one above; exactly full and one over);
- check the **exact** error message, not just `is not None`;
- test `max_party` with a value other than the default.

When there are no survivors, commit your work and merge it:

1. Run `uv run pytest` to check every test passes.
2. Add the `mutants/` folder to `.gitignore`. It is generated output, so it should not be committed:

   ```bash
   echo "mutants/" >> .gitignore
   ```

3. Run `git status`. You should see changes to `.gitignore`, `pyproject.toml`, `uv.lock` and `app/bookings.py`, and the new files `app/booking_rules.py` and `tests/test_booking_rules.py`. If `mutants/` is listed, check step 2.
4. Commit in two steps, so your history shows the refactoring separately from the tests:

   ```bash
   git add app/booking_rules.py app/bookings.py
   git commit -m "Extract booking rules into plain functions"
   git add .gitignore pyproject.toml uv.lock tests/test_booking_rules.py
   git commit -m "Add mutation testing and tests that kill every mutant"
   ```

5. Push the branch: `git push -u origin test/effectiveness`
6. Open a pull request from `test/effectiveness` to `main` (GitHub shows a prompt after you push, or run `gh pr create`). In the description, say what you changed and give your mutation score before and after, for example "6 of 16 mutants killed before, 16 of 16 after". There is no issue to close this time.
7. Merge the pull request, then update your local copy: `git switch main && git pull`

## Checkpoint

`uv run mutmut results` shows no survivors, and you can explain why coverage alone could not have told you the original tests were weak.

## Apply it to Assignment 1

Measure coverage on your assignment feature before you start: you will probably find it is already high. Extract the rules of your feature into plain functions so you can test and mutate them, and keep a note of your mutation score before and after improving your tests. That before-and-after evidence is exactly what the Testing and Code Quality criteria reward.

## Stretch

Plant a fault deliberately (for example change `max_party` to `5`), run the suite to show it fails, then undo it. This **seeded fault** technique is a quick alternative when mutation testing is not available.