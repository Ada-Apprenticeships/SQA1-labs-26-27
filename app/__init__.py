"""Events application factory."""
from flask import Flask

from .extensions import csrf, db


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    if config:
        app.config.update(config)

    db.init_app(app)
    csrf.init_app(app)

    from . import auth, events
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)

    from .cli import register_cli
    register_cli(app)

    return app
