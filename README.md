# Ada Events: SQA1 practice repository

This repository is for the **Software Quality Assurance labs**. It is a small Flask site where people can browse upcoming events.

A colleague has just added a first draft of a new **bookings** feature, written quickly with an AI coding assistant. Over the labs you will take that feature from draft to production quality, practising the same steps you will use in Assignment 1.

The lab instructions are in the [`labs`](labs/README.md) folder. Start with Lab 0.

## Quick start (GitHub Codespaces)

1. Choose **Code → Codespaces → Create codespace on main**.
2. Wait for setup to finish.
3. Run `uv run flask --app run run --debug` and open the preview on port 5000.

Seeded users: `alice` (organiser of every event), `bob` and `carol`. All passwords are `password123`.

## Own machine

```bash
uv sync
uv run flask --app run init-db
uv run flask --app run seed
uv run flask --app run run --debug
uv run pytest
```

If you cannot install uv: `python -m venv .venv`, activate it, `pip install -r requirements.txt`, then run the same commands without `uv run`.
