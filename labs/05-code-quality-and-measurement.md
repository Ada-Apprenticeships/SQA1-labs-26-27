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

### Reading the results

Each command gives you one number for the table:

- **`ruff check`** (Ruff lint findings). Ruff lists every problem it finds, such as unused imports or imports out of order. Each one starts with a rule code (for example `I001`), and `[*]` means Ruff can fix it automatically. The list can be long, so the number you need is on the **last line**: `Found N errors`. For a one-line summary per rule instead, add `--statistics`.
- **`ruff format --check`** (files needing reformatting). This checks layout only (spacing, line breaks, quotes) and changes nothing. Record the number from `N files would be reformatted`.
- **`radon cc`** (complexity of `book()`). Find the line for `book`, for example `F 19:0 book - A (4)`. `F` means function, `19:0` is where it starts, `A` is the grade, and the number in brackets is its **cyclomatic complexity**: the number of independent paths through the code. Each `if` adds one. Lower is simpler and easier to test. Grade A is 1 to 5, B is 6 to 10, and anything above 10 is worth refactoring. Record the number and grade, for example `4 (A)`.
- **`radon mi`** (maintainability index of `bookings.py`). Find the line for `bookings.py`, for example `bookings.py - A (68.00)`. The maintainability index runs from 0 to 100, combining size, complexity and comments, and **higher is better**. Record the number in brackets. Ignore the other files for now.
- **Coverage and mutation score.** These come from Lab 3. For the draft, use the coverage you measured at the start of Lab 3 and your mutation score before you added tests (for example, 6 of 16 mutants killed). You will measure them again for the Now column.
- **Open defect issues.** Count the open issues on your repository's **Issues** tab. For the draft, count every defect you logged in Lab 1.

Record the results in a table like this one:

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

Review what `--fix` and `format` changed with `git diff` before committing: automated fixes still need checking. Then run the tests, and commit the tools, configuration and clean-up together:

```bash
uv run pytest
git add pyproject.toml uv.lock app tests
git commit -m "Add Ruff and radon; apply lint fixes and formatting"
```

Most files will be in this commit, because `ruff format` touches nearly all of them. That is expected.

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

Run `uv run pytest tests/test_events.py`. It **fails**: the page shows 4 places left, not 1. Commit the failing test on its own:

```bash
git add tests/test_events.py
git commit -m "Add failing test for places left (#N)"
```

Replace `N` with the number of the issue you logged for this in Lab 1. If you did not log one, create it now.

Now fix it. Add a property to the `Event` model in `app/models.py`, directly under its `bookings` relationship:

```python
    @property
    def places_left(self):
        from .booking_rules import places_remaining
        return places_remaining(self.capacity, [b.party_size for b in self.bookings])
```

Then use it in `app/templates/event.html`. Find this line, about line 8:

```jinja
    <p class="meta">Places left: {{ event.capacity - event.bookings|length }} of {{ event.capacity }}</p>
```

and replace it with:

```jinja
    <p class="meta">Places left: {{ event.places_left }} of {{ event.capacity }}</p>
```

Only the calculation changes: the template now asks the model for `places_left` instead of working it out itself.

Run `uv run pytest`: every test should now pass. Commit the fix:

```bash
git add app/models.py app/templates/event.html
git commit -m "Use the booking rules for places left (fixes #N)"
```

Then run `git status`: there should be nothing left to commit before you start section 5.

## 5. Your turn

**1. Create `QUALITY.md`.** In the top folder of your repository, create a file called `QUALITY.md`. Give it a heading, such as `# Quality measurements`, and paste in your table with the Draft column filled in.

**2. Measure your current code.** Run the same commands as in section 2, but on `app` instead of `../draft/app`:

```bash
uv run ruff check app
uv run ruff format --check app
uv run radon cc app/bookings.py -s
uv run radon mi app -s
```

After section 3, `ruff check` should report `All checks passed!` and `ruff format --check` should report that every file is `already formatted`, so record 0 for both.

Then measure coverage and mutation score:

```bash
uv run pytest --cov=app
rm -rf mutants && uv run mutmut run
```

- **Coverage:** use the percentage on the `TOTAL` line, in the `Cover` column.
- **Mutation score:** use the counts on mutmut's progress line: killed (🎉) out of the total, for example `16 of 16`.
- **Open defect issues:** count the open issues on your repository's **Issues** tab.

Fill in the **Now** column.

**3. Interpret it.** Under the table, write three or four sentences. Which measures improved? Which barely moved? Most importantly: **the draft already had a good complexity score and high coverage, yet it was full of defects. What does that tell you about relying on these measures?**

**4. Commit, push and merge.**

```bash
git add QUALITY.md
git commit -m "Add before-and-after quality measurements"
git push -u origin quality/measurement
```

Open a pull request from `quality/measurement` to `main` (GitHub shows a prompt after you push, or run `gh pr create`). In the description, summarise what you changed in this lab: the Ruff fixes and formatting, and the `places_left` refactoring. Merge it, then run `git switch main && git pull`.

## Checkpoint

You have a before-and-after table with an honest interpretation, the duplicated rule is gone, and Ruff reports no findings.

## Apply it to Assignment 1

Take your baseline measurements of your assignment draft **before** you change anything, so you can show improvement later. Choose one refactoring that improves maintainability or testability and be ready to explain it in your video.

## Stretch

Run `uv run radon cc app -s -a` to see the average complexity across the whole app, and find the most complex function. Does it need refactoring, or is the complexity justified?