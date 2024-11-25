from typing import Generator, List

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, relationship, sessionmaker

from app.config import settings

Base = declarative_base()


class User(Base):
    """
    Represents a user of the application.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username chosen by the user.
        password_hash (str): Hashed password for user authentication.
        email (str): Unique email associated with the user account.
        created_at (datetime): Date and time when the user account was created.
        is_active (bool): Indicates if the user's account is active.
    """

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)

    challenges: Mapped[List["Challenge"]] = relationship(
        "Challenge", back_populates="user"
    )


class Challenge(Base):
    """
    Represents a user-created challenge or task the user aims to track.

    Attributes:
        id (int): Unique identifier for the challenge.
        user_id (int): Foreign key linking the challenge to a specific user.
        name (str): Name of the challenge.
        description (str): Additional information describing the challenge.
        started_at (datetime): Date and time when the challenge started.
        completed_at (datetime): Date and time when the challenge was completed, if applicable.
    """

    __tablename__ = "challenges"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    started_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="challenges")
    daily_logs: Mapped[List["DailyLog"]] = relationship(
        "DailyLog", back_populates="challenge", cascade="all, delete-orphan"
    )


class DailyLog(Base):
    """
    Represents a log entry for daily tracking of a challenge.

    Attributes:
        id (int): Unique identifier for the daily log entry.
        challenge_id (int): Foreign key linking the log to a specific challenge.
        log_date (datetime): The date of the log entry.
        completed (bool): Indicates whether the challenge was completed on this date.
        created_at (datetime): Timestamp for when the log entry was created.
        updated_at (datetime): Timestamp for when the log entry was last updated.
    """

    __tablename__ = "daily_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    challenge_id = Column(BigInteger, ForeignKey("challenges.id"), nullable=False)
    log_date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)  # Default to False
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    challenge: Mapped["Challenge"] = relationship(
        "Challenge", back_populates="daily_logs"
    )


class SharedChallenge(Base):
    """
    Represents a challenge shared between users.

    Attributes:
        id (int): Unique identifier for the shared challenge record.
        challenge_id (int): Foreign key linking to the shared challenge.
        shared_user_id (int): Foreign key linking to the user the challenge is shared with.
        shared_at (datetime): Date and time when the challenge was shared.
    """

    __tablename__ = "shared_challenges"

    id = Column(BigInteger, primary_key=True, index=True)
    challenge_id = Column(BigInteger, ForeignKey("challenges.id"), nullable=False)
    shared_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    shared_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    challenge: Mapped["Challenge"] = relationship("Challenge", backref="shared_with")
    shared_user: Mapped["User"] = relationship("User", backref="shared_challenges")


# Create the SQLAlchemy engine to connect to the database
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for each request and ensures it is closed afterward.

    Yields:
        Session: The SQLAlchemy database session.
    """
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Provide the session to the request handler
    finally:
        db.close()  # Ensure the session is closed after the request
