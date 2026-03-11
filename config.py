import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "tradeflow-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///tradeflow.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
