import os


class Config:
    BASE_DIR = os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))
    )

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "insider-threat-development-secret"
    )

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///"
        + os.path.join(BASE_DIR, "instance", "insider_threat.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False