# Lab 0: Set up and explore

**Aim:** get the repository running, understand what is in it, and learn to read its history.
**Time:** about 30 minutes.

## 1. Open a codespace

1. On your copy of this repository, choose **Code → Codespaces → Create codespace on main**.
2. Wait for setup to finish. It installs [uv](https://docs.astral.sh/uv/), installs the dependencies, creates the database and adds sample data.

Working on your own machine instead? Follow the README in the repository root.

## 2. Run the tests

```bash
uv run pytest
```

You should see all tests pass. Keep that in mind: passing tests do not mean the feature works.

## 3. Run the app

```bash
uv run flask --app run run --debug
```

The app opens in a new browser tab (port 5000). If it does not, open the **Ports** tab and click the globe icon next to port 5000. Log in as `bob` (password `password123`), open an event and make a booking. Then log out and log in as `alice`, who organises every event, and look at the attendee list.

Stop the app with `Ctrl+C` when you are done.

## 4. Read the history

The commit history tells you what changed and who changed it. Inherited code always deserves this step.

```bash
git log --oneline
git show --stat HEAD
git show HEAD -- app/bookings.py
```

`git show --stat HEAD` lists every file the bookings draft touched. Make a note of them: they are the scope of your inspection in Lab 1.

## 5. Tidy up

Close the app's browser tab and press Ctrl+C in the terminal to stop the server. When you finish for the day, stop your codespace from **Code → Codespaces → ⋯ → Stop codespace** to save your free hours.

## Apply it to Assignment 1

Do the same for your assignment repository now: open a codespace, run the tests, run the app, and use `git log` and `git show` to find exactly which files the draft for your chosen feature changed.
