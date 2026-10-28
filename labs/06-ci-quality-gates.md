# Lab 6: Continuous integration as a quality gate

**Aim:** make GitHub Actions run every quality check on every pull request, and block changes that fail.
**Time:** about 75 minutes.
**Assignment 1 criterion:** CI/CD and Git Practices.

## 1. Read the current workflow

Open `.github/workflows/ci.yml`. It only runs on pushes to `main` and only runs the tests. By the time it runs, a defect is already on `main`. A **quality gate** checks a change **before** it is merged.

## 2. Write the quality gate

```bash
git switch main && git pull
git switch -c ci/quality-gates
```

Replace the contents of `.github/workflows/ci.yml` with:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check .

      - name: Check formatting
        run: uv run ruff format --check .

      - name: Tests with coverage threshold
        run: uv run pytest --cov=app --cov-fail-under=85

      - name: Security scan (code)
        run: uv run bandit -r app -ll

      - name: Security scan (dependencies)
        run: uv run pip-audit
```

Each step is a gate: if any command fails, the whole check fails. `--cov-fail-under=85` fails the build if coverage drops below 85%, and `-ll` makes Bandit fail only on medium or high severity findings.

Check your current coverage with `uv run pytest --cov=app` first. If it is below 85%, set the threshold just below your figure for now and add tests to raise it.

Run the same commands locally, so you know the pipeline will pass:

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest --cov=app --cov-fail-under=85 && uv run bandit -r app -ll && uv run pip-audit
```

Commit, push and open a pull request. Open the **Checks** tab on the pull request and watch the `quality` job run. Merge once it is green.

## 3. Protect the main branch

A gate only works if it cannot be skipped. On GitHub, go to **Settings → Rules → Rulesets → New ruleset → New branch ruleset**:

1. Name it `Protect main` and set **Enforcement status** to **Active**.
2. Under **Target branches**, add **Include default branch**.
3. Tick **Require a pull request before merging**.
4. Tick **Require status checks to pass**, then **Add checks** and choose `quality`.
5. Save.

If these settings are not available, your organisation's plan does not support rulesets on private repositories. Carry on with step 4 anyway: the failing check is still visible on the pull request, and you can explain in your video how you would protect the branch.

## 4. See the gate block a bad change

```bash
git switch main && git pull
git switch -c demo/blocked-change
```

Deliberately break something. In `app/booking_rules.py`, change `MAX_PARTY = 4` to `MAX_PARTY = 5`. Commit, push and open a pull request. The `quality` check fails because your tests catch the change, and with the ruleset active the **Merge** button is blocked.

Take a screenshot: this is exactly the evidence the CI/CD criterion asks for. Then fix it by pushing a commit that restores the value, watch the check turn green, and close or merge the pull request.

## 5. Your turn

1. Make sure every open issue from Lab 1 is either closed by a pull request (`Fixes #n`) or has a comment explaining why it is deferred.
2. Look at your Git history with `git log --oneline --graph` and check that it tells a clear story: branch per change, tests before fixes, descriptive messages.

## Checkpoint

Every pull request is checked automatically by lint, formatting, tests with a coverage threshold and two security scans, and you have evidence of a pull request being blocked by a failing check.

## Apply it to Assignment 1

Set up the same gate on your assignment repository **early**, so that every fix you make afterwards is checked by it. Choose your coverage threshold honestly: set it just below what you have achieved, so it protects against going backwards.

## Stretch

Add a step that uploads the coverage report as an artifact (`actions/upload-artifact`), or a job that runs mutation testing on pull requests that change `app/booking_rules.py`.
