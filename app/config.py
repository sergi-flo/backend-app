import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    Attributes:
        DATABASE_URL (str): Database connection URL.
        SECRET_KEY (str): Secret key for application security.
        ALGORITHM (str): Algorithm used for hashing and token generation.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Duration in minutes for token expiration.
    """

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:12345@daily_challenges_db/daily_challenges",
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"  # Load settings from a .env file


# Initialize settings object
settings = Settings()
