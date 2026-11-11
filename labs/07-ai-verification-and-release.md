# Lab 7: Verifying AI output and making a release recommendation

**Aim:** use AI tools responsibly, measure the quality of what they produce, record their use, and make a justified decision about whether the feature is ready to release.
**Time:** about 75 minutes.
**Assignment 1 criteria:** all, especially the release recommendation and the AI requirements.

## 1. Ask an AI tool to write tests

```bash
git switch main && git pull
git switch -c test/ai-generated
```

Using any AI assistant (for example GitHub Copilot Chat in your codespace), ask:

> Write pytest tests for `places_remaining` and `booking_error` in `app/booking_rules.py`.

Save what it produces as `tests/test_booking_rules_ai.py`, unchanged. Run it with `uv run pytest tests/test_booking_rules_ai.py`. Do the tests pass? Do any of them test things the code was never meant to do?

## 2. Measure the AI's tests

Point mutmut at the AI tests only, by changing the test selection in `pyproject.toml`:

```toml
pytest_add_cli_args_test_selection = ["tests/test_booking_rules_ai.py"]
```

```bash
rm -rf mutants
uv run mutmut run
uv run mutmut results
```

Compare the number of surviving mutants with your own tests from Lab 3. Then switch the selection back to `tests/test_booking_rules.py`.

Write down three things in your notes:

1. the AI tests' mutation score compared with yours;
2. one test the AI wrote that was weak or wrong, and why;
3. one useful idea from the AI that you had not thought of.

This is **verification**: you use AI output on the strength of evidence, not because it looks right.

## 3. Record AI use in pull requests

You have been filling in the AI section of your pull request template since Lab 2. This pull request is the one where it matters most, so make it a good model for Assignment 1.

**1. Improve the AI's tests.** Edit `tests/test_booking_rules_ai.py`, using your notes from section 2:

- delete any test that checks behaviour the requirements never asked for, or correct it to match R1 to R7;
- strengthen weak tests, for example by checking the exact error message instead of `is not None`;
- keep the useful ideas.

Check that the test selection in `pyproject.toml` is back to `tests/test_booking_rules.py`.

**2. Run the checks your pipeline will run.** AI-generated code often does not match a project's style, so let Ruff tidy it before the Lab 6 gate rejects it:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run pytest
```

**3. Commit and push:**

```bash
git add tests/test_booking_rules_ai.py
git commit -m "Add AI-suggested tests for booking rules, verified and improved"
git push -u origin test/ai-generated
```

**4. Open a pull request** from `test/ai-generated` to `main`, and fill in the template:

- **What this changes:** one or two sentences. There is no issue for this change, so delete the `Fixes #` line.
- **How I tested it:** for example, the tests pass and your mutation testing results.
- **AI assistance:** tick "AI was used for", then say honestly what the AI did and how you checked it, with evidence. For example: "Copilot suggested tests for booking_rules. Mutation testing showed six survivors; I rewrote the boundary tests and kept its test for an empty bookings list."

Merge once the `quality` check is green.

## 4. Make a release recommendation

Start a new branch from the updated `main`:

```bash
git switch main && git pull
git switch -c docs/release-recommendation
```

Imagine the product owner asks: **"Can we release bookings on Monday?"** Using your evidence from Labs 1 to 6, write a short recommendation (about 200 words) in `QUALITY.md`, covering:

- **Your answer:** release, release with conditions, or do not release.
- **Evidence:** which defects are fixed and how you know (tests, mutation score, scans, the CI gate).
- **Residual risks:** what is still open or deferred, and why that is or is not acceptable.
- **Limits of your evidence:** what your tests and tools could not tell you, for example how the site behaves with many simultaneous bookings, or how accessible it is.

There is no single right answer. A justified "do not release yet" can be stronger than an unjustified "yes".

**Don't forget to commit and merge your `QUALITY.md`.** Your `main` branch is protected, so it goes through a pull request like everything else:

```bash
git add QUALITY.md
git commit -m "Add release recommendation"
git push -u origin docs/release-recommendation
```

Open a pull request, fill in the template (no issue, so delete the `Fixes #` line), and merge once the `quality` check is green. Then run `git switch main && git pull`.

## Checkpoint

You have measured AI-generated tests against your own, recorded how you checked them in a pull request, and merged a written release recommendation backed by evidence.

To compare your work with a finished version, including a sample release recommendation and every pull request description, download the [labs exemplar](https://staticwebsitesjr.z33.web.core.windows.net/sqa1/sqa1-labs-exemplar.zip). Think about why each step was done, not just what was done.

## Apply it to Assignment 1

You are now ready to start Assignment 1 properly. You have already practised the same process on different code; the only difference is the feature and its defects. Read the brief's AI section again: in the assignment, AI use must be disclosed in every pull request and verified, exactly as in this lab.