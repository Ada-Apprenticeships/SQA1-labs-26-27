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

If any of them fails, fix it before you go on. Then:

1. Commit the workflow and push your branch:

   ```bash
   git add .github/workflows/ci.yml
   git commit -m "Add CI quality gates: lint, format, coverage and security scans"
   git push -u origin ci/quality-gates
   ```

   If you changed the coverage threshold or added tests, add those files too.

2. Open a pull request from `ci/quality-gates` to `main` (GitHub shows a prompt after you push, or run `gh pr create`).
3. Watch the check run. Near the bottom of the pull request's **Conversation** tab, a box lists `CI / quality (pull_request)`. A yellow dot means it is running, which takes a minute or two. For the detail, open the **Checks** tab and click `quality`: each step from `ci.yml` is listed, and you can expand any step to see its output.
4. If it turns **red**, open the **Checks** tab, find the step with the red cross and expand it to see the error. Fix the problem in your codespace, run the local command above again, then commit and push to the same branch. The check runs again automatically.
5. When it is **green**, merge the pull request, then run `git switch main && git pull`.

The workflow runs again on `main` after the merge, because of the `push` trigger. You can see every run on the repository's **Actions** tab.

## 3. Protect the main branch

A gate only works if it cannot be skipped. On GitHub, go to **Settings → Rulesets** (under **Code and automation** in the left menu), then **New ruleset → New branch ruleset**:

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

Now deliberately reintroduce the overbooking defect from Lab 1, as if someone had made a careless change:

1. In `app/booking_rules.py`, find this line in `booking_error()`:

   ```python
       if party_size > places_remaining(capacity, party_sizes):
   ```

   and add `+ 1` back, so it reads:

   ```python
       if party_size > places_remaining(capacity, party_sizes) + 1:
   ```

2. Run `uv run pytest`. It fails: your tests from Labs 2 and 3 catch the regression. Normally you would stop here, but this time commit it anyway to see what the pipeline does:

   ```bash
   git add app/booking_rules.py
   git commit -m "Demo: reintroduce the overbooking defect"
   git push -u origin demo/blocked-change
   ```

3. Open a pull request from `demo/blocked-change` to `main`.
4. Watch the `quality` check. After a minute or two it shows a **red cross**. On the **Checks** tab, expand the **Tests with coverage threshold** step to see which tests failed and why.
5. Go back to the **Conversation** tab and scroll to the bottom. With the ruleset active, GitHub says merging is blocked because a required status check has failed, and the **Merge** button cannot be used.

**Take a screenshot** showing the failed check and the blocked merge. This is exactly the evidence the CI/CD criterion asks for.

Then undo the damage:

6. Remove the `+ 1` again, run `uv run pytest` to check everything passes, then commit and push to the same branch:

   ```bash
   git add app/booking_rules.py
   git commit -m "Remove the reintroduced overbooking defect"
   git push
   ```

7. Watch the check run again and turn **green**. The branch now makes no real change, so **close** the pull request without merging, and delete the branch when GitHub offers.
8. Return to `main`: `git switch main && git pull`

## 5. Your turn

1. Make sure every open issue from Lab 1 is either closed by a pull request (`Fixes #n`) or has a comment explaining why it is deferred.
2. Look at your Git history with `git log --oneline --graph` and check that it tells a clear story: branch per change, tests before fixes, descriptive messages.

Need to catch up, or not sure how? The [Lab 6 catch-up sheet](https://staticwebsitesjr.z33.web.core.windows.net/sqa1/sqa1-lab6-catch-up.html) shows where each Lab 1 defect is fixed, how to close or defer issues properly, and what a clear history looks like.

## Checkpoint

Every pull request is checked automatically by lint, formatting, tests with a coverage threshold and two security scans, and you have evidence of a pull request being blocked by a failing check.

## Apply it to Assignment 1

Set up the same gate on your assignment repository **early**, so that every fix you make afterwards is checked by it. Choose your coverage threshold honestly: set it just below what you have achieved, so it protects against going backwards.

## Stretch (optional)

Add a step that uploads the coverage report as an artifact (`actions/upload-artifact`), or a job that runs mutation testing on pull requests that change `app/booking_rules.py`.