"""Application configuration."""
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-for-local-use-only")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///events.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
