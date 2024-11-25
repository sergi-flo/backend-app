from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        username (str): Unique username for the user.
        password (str): Plain text password (will be hashed).
        email (str): User's email address.
    """

    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)
    email: EmailStr


class UserResponse(BaseModel):
    """
    Schema for representing a user in responses.

    Attributes:
        id (int): Unique user identifier.
        username (str): User's username.
        email (str): User's email.
        created_at (datetime): Account creation date.
    """

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """
    Schema to login a user.

    Attributes:
        username (str): Unique username for the user.
        password (str): Plain text password (will be hashed).
    """

    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)


# Challenge Schemas
class ChallengeCreate(BaseModel):
    """
    Schema for creating a new challenge.

    Attributes:
        name (str): Challenge name.
        description (str): Detailed description of the challenge.
    """

    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class ChallengeResponse(BaseModel):
    """
    Schema for representing a challenge in responses.

    Attributes:
        id (int): Unique challenge identifier.
        name (str): Name of the challenge.
        description (str): Description of the challenge.
        started_at (datetime): Start date of the challenge.
        completed_at (Optional[datetime]): Completion date of the challenge, if applicable.
    """

    id: int
    name: str
    description: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True


# DailyLog Schemas
class DailyLogCreate(BaseModel):
    """
    Schema for creating a daily log entry.

    Attributes:
        log_date (date): Date of the log entry.
        completed (bool): Indicates if the task was completed.
        challenge_id (int): ID of the challenge being logged.
    """

    log_date: date
    completed: bool
    challenge_id: int


class DailyLogUpdate(BaseModel):
    """
    Schema for updating a daily log entry.

    Attributes:
        completed (bool): Indicates if the task was completed.
    """

    completed: bool


class DailyLogResponse(BaseModel):
    """
    Schema for representing a daily log entry in responses.

    Attributes:
        id (int): Unique identifier for the daily log.
        log_date (date): Date of the log entry.
        completed (bool): Indicates if the challenge was completed on this date.
    """

    id: int
    challenge_id: int
    log_date: date
    completed: bool

    class Config:
        orm_mode = True


# SharedChallenge Schemas
class SharedChallengeCreate(BaseModel):
    """
    Schema for creating a shared challenge entry.

    Attributes:
        challenge_id (int): ID of the challenge to be shared.
        shared_user_id (int): ID of the user the challenge is shared with.
    """

    challenge_id: int
    shared_user_id: int


class SharedChallengeResponse(BaseModel):
    """
    Schema for representing a shared challenge in responses.

    Attributes:
        id (int): Unique identifier for the shared challenge record.
        challenge_id (int): ID of the challenge being shared.
        shared_user_id (int): ID of the user with whom the challenge is shared.
        shared_at (datetime): Date and time when the challenge was shared.
    """

    id: int
    challenge_id: int
    name: str
    description: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    shared_at: datetime
    shared_by: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    """
    Schema for representing a JWT access token response.

    Attributes:
        access_token (str): The JWT access token for the authenticated user.
        token_type (str): The type of the token, typically 'bearer'.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for representing the payload data contained in a JWT token.

    Attributes:
        id (int): The unique identifier of the user to whom the token belongs.
    """

    id: int
    username: str
