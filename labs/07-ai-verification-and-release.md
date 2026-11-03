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

Create `.github/pull_request_template.md` so every pull request asks the question:

```markdown
## What this changes

Fixes #

## How I tested it

## AI assistance

- [ ] No AI was used for this change
- [ ] AI was used for:

How I checked the AI output:
```

Commit it with your improved tests (keep the AI's useful ideas, drop or fix the weak ones) and open a pull request. Fill in the AI section honestly, for example: "Copilot suggested tests for booking_rules. Mutation testing showed six survivors; I rewrote the boundary tests and kept its test for an empty bookings list."

## 4. Make a release recommendation

Imagine the product owner asks: **"Can we release bookings on Monday?"** Using your evidence from Labs 1 to 6, write a short recommendation (about 200 words) in `QUALITY.md`, covering:

- **Your answer:** release, release with conditions, or do not release.
- **Evidence:** which defects are fixed and how you know (tests, mutation score, scans, the CI gate).
- **Residual risks:** what is still open or deferred, and why that is or is not acceptable.
- **Limits of your evidence:** what your tests and tools could not tell you, for example how the site behaves with many simultaneous bookings, or how accessible it is.

There is no single right answer. A justified "do not release yet" can be stronger than an unjustified "yes".

## Checkpoint

You have measured AI-generated tests against your own, a pull request template with an AI section, and a written release recommendation backed by evidence.

## Apply it to Assignment 1

You are now ready to start Assignment 1 properly. You have already practised the same process on different code; the only difference is the feature and its defects. Read the brief's AI section again: in the assignment, AI use must be disclosed in every pull request and verified, exactly as in this lab.