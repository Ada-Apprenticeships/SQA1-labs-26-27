# Lab 5: Code quality and measurement

**Aim:** use linting, formatting and complexity tools; remove duplicated logic; and show improvement with before-and-after measures, interpreting what they do and do not tell you.
**Time:** about 60 minutes.
**Assignment 1 criterion:** Code Quality and Measurement.

## 1. Add the tools

```bash
git switch main && git pull
git switch -c quality/measurement
uv add --dev ruff radon
```

**Ruff** is a fast linter and formatter (it replaces flake8 and black). **Radon** measures complexity and maintainability. Configure Ruff by adding this to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
extend-exclude = ["labs"]

[tool.ruff.lint]
select = ["E", "F", "I", "B"]
```

`E` and `F` are style errors and likely bugs, `I` sorts imports, and `B` catches common bug patterns. `extend-exclude` stops Ruff touching the code snippets in these lab instructions, which it would otherwise reformat.

## 2. Measure the original draft

To show improvement you need a **baseline**. Check out the draft as it was, in a separate folder, without disturbing your branch:

```bash
git worktree add ../draft $(git log --format=%h --grep="Add event bookings" -1)
uv run ruff check ../draft/app
uv run ruff format --check ../draft/app
uv run radon cc ../draft/app/bookings.py -s
uv run radon mi ../draft/app -s
```

Record the results in a table like this one, alongside your coverage and mutation figures from Lab 3:

| Measure | Draft | Now |
|---|---|---|
| Ruff lint findings | | |
| Files needing reformatting | | |
| Complexity of `book()` (radon cc) | | |
| Maintainability index of `bookings.py` (radon mi) | | |
| Test coverage of `app` | | |
| Mutation score of booking rules | | |
| Open defect issues | | |

Remove the extra folder when you are done: `git worktree remove ../draft`.

## 3. Lint and format your current code

```bash
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .
```

Review what `--fix` and `format` changed with `git diff` before committing: automated fixes still need checking.

## 4. Remove duplicated logic (worked example)

The event page shows "places left" using its own calculation:

```jinja
Places left: {{ event.capacity - event.bookings|length }}
```

It counts **bookings**, not **places**, so one booking for 4 people only reduces it by 1. The booking rules from Lab 3 calculate it correctly. Two versions of the same rule will always drift apart, so have one source of truth.

First, a failing test. Add `from conftest import login` to the imports at the top of `tests/test_events.py`, then add this test at the end:

```python
def test_places_left_counts_places_not_bookings(client, alice, bob, event):
    login(client, "bob")
    client.post(f"/events/{event.id}/book", data={"party_size": "4"})
    response = client.get(f"/events/{event.id}")
    assert b"Places left: 1 of 5" in response.data
```

Then add a property to the `Event` model in `app/models.py`, directly under its `bookings` relationship:

```python
    @property
    def places_left(self):
        from .booking_rules import places_remaining
        return places_remaining(self.capacity, [b.party_size for b in self.bookings])
```

and use it in `app/templates/event.html`:

```jinja
Places left: {{ event.places_left }} of {{ event.capacity }}
```

Run the tests, then commit.

## 5. Your turn

1. Fill in the **Now** column of your table.
2. Under the table, write three or four sentences interpreting it. Which measures improved? Which barely moved? Most importantly: **the draft already had a good complexity score and high coverage, yet it was full of defects. What does that tell you about relying on these measures?**
3. Save the table and your interpretation in a file called `QUALITY.md`, commit it, and merge your pull request.

## Checkpoint

You have a before-and-after table with an honest interpretation, the duplicated rule is gone, and Ruff reports no findings.

## Apply it to Assignment 1

Take your baseline measurements of your assignment draft **before** you change anything, so you can show improvement later. Choose one refactoring that improves maintainability or testability and be ready to explain it in your video.

## Stretch

Run `uv run radon cc app -s -a` to see the average complexity across the whole app, and find the most complex function. Does it need refactoring, or is the complexity justified?
