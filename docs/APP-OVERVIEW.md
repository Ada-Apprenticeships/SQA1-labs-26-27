# App overview: what each file and function does

A quick map of the Ada Events app, so you know where to look. It describes what each part is **meant** to do. Whether it actually does it is what the labs are for.

## How a request flows

1. `run.py` builds the app with `create_app()`.
2. A browser request arrives, for example `POST /events/3/book`.
3. Flask matches the URL to a route function in one of the **blueprints** (`auth`, `events`, `bookings`).
4. The route reads the form or URL, uses the **models** to read or change the database, then either renders a **template** or redirects.

## `run.py`

- `app = create_app()`: the entry point that `flask --app run` uses.

## `app/__init__.py`

- `create_app(config=None)`: builds the Flask app, loads the settings, switches on the database and CSRF protection, and registers the three blueprints and the CLI commands. Tests pass their own `config` to use a temporary database.

## `app/config.py`

- `Config`: default settings (secret key, database location). Environment variables override them.

## `app/extensions.py`

- `db`: the SQLAlchemy database object shared across the app.
- `csrf`: Flask-WTF's CSRF protection, which rejects form posts without a valid token.

## `app/models.py`

- `utcnow()`: the current time in UTC, in the form SQLite stores.
- `User`: a registered user (username and hashed password).
  - `set_password(password)`: hashes the password and stores the hash, never the password itself.
  - `check_password(password)`: checks a typed password against the stored hash.
- `Event`: an event with a title, description, location, start time, capacity and organiser. `event.bookings` lists its bookings.
- `Booking`: one user's booking for one event, with a party size, an optional note and when it was made.

## `app/auth.py`

- `load_logged_in_user()`: runs before every request and puts the logged-in user (or `None`) in `g.user`.
- `login_required(view)`: a decorator that sends anyone not logged in to the login page.
- `register()`: shows the sign-up form and creates a new user.
- `login()`: shows the login form, checks the password and stores the user's id in the session.
- `logout()`: clears the session.

## `app/events.py`

- `index()`: the home page (`/`), listing upcoming events in date order.
- `view(event_id)`: the page for one event (`/events/<id>`), including the booking form.

## `app/bookings.py`

The new feature, drafted with an AI coding assistant.

- `MAX_PARTY`: the most places one booking can take.
- `book(event_id)`: handles the booking form; checks the party size and remaining places, then saves the booking.
- `mine()`: the "My bookings" page (`/bookings`). The name means "my bookings"; it lists the logged-in user's bookings, with an optional search by event title.
- `cancel(booking_id)`: cancels a booking.

## `app/cli.py`

- `register_cli(app)`: adds two terminal commands to the app.
  - `init-db`: deletes and recreates all the tables.
  - `seed`: adds three users (`alice`, `bob`, `carol`, password `password123`) and six events, one of them in the past.

## `app/templates/`

The HTML pages, filled in by the route functions.

- `base.html`: the shared layout (navigation bar, flash messages).
- `index.html`, `event.html`: the events list and a single event with its booking form.
- `my_bookings.html`: the user's bookings, with the search box and cancel buttons.
- `login.html`, `register.html`: the login and sign-up forms.

## `tests/conftest.py`

pytest loads this file automatically and shares its fixtures with every test file.

- `app`: a fresh app with an empty in-memory database for each test (CSRF switched off so tests can post forms).
- `client`: a pretend browser for sending requests to the app.
- `alice`, `bob`: ready-made users.
- `event`: an upcoming event organised by Alice, with a capacity of 5.
- `make_user(name)`: a helper that creates a user with the password `password123`.
- `login(client, username)`: a helper that logs a user in through the real login form.

## `tests/`

- `test_auth.py`: registering, a too-short password, a wrong password and a successful login.
- `test_events.py`: the home page lists upcoming events and hides past ones; the event page shows its details.
- `test_bookings.py`: a starter set of booking tests. They are thin on purpose: Labs 2 and 3 show you why and how to improve them.

## Added during the labs

- `app/booking_rules.py` (Lab 3): `places_remaining()` and `booking_error()`, the booking rules pulled out of `book()` so they can be unit tested on their own.

See also the [testing toolkit](https://staticwebsitesjr.z33.web.core.windows.net/sqa1/sqa1-testing-toolkit.html) for how to write tests against these functions.