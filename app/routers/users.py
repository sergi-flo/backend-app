from datetime import timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, schemas
from app.config import settings
from app.schemas import TokenData
from app.utils import create_access_token, oauth2_scheme, verify_token

router = APIRouter()


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: schemas.UserCreate, db: Session = Depends(database.get_db)
) -> database.User:
    """
    Create a new user in the system.

    Args:
        user (schemas.UserCreate): User data to create a new user.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.UserResponse: Created user details.
    """
    # Check if user with the same username or email already exists
    existing_user = (
        db.query(database.User)
        .filter(
            (database.User.username == user.username)
            | (database.User.email == user.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username or email already exists.",
        )

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = database.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password.decode("utf-8"),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/token", response_model=schemas.Token)
def login(
    user: schemas.UserLogin, db: Session = Depends(database.get_db)
) -> dict[str, str]:
    """
    Authenticate a user and return a JWT token.

    Args:
        user (schemas.UserCreate): User credentials for authentication.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.Token: JWT access token for the authenticated user.
    """
    db_user = (
        db.query(database.User).filter(database.User.username == user.username).first()
    )
    if db_user is None or not bcrypt.checkpw(
        user.password.encode("utf-8"), db_user.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=schemas.Token)
def refresh_token(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """
    Refresh the JWT token if it is about to expire.

    Args:
        token (str): The current JWT token to refresh.

    Returns:
        schemas.Token: New JWT token with extended expiration.
    """
    payload = verify_token(token)
    new_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": payload.username, "id": payload.id},
        expires_delta=new_access_token_expires,
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemas.UserResponse)
def get_current_user(
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(database.get_db),
) -> database.User:
    """
    Retrieve the profile of the current authenticated user.

    This endpoint uses the JWT token to identify the user and return their profile data.

    Args:
        current_user (TokenData): Token data extracted from the validated JWT token.
        db (Session): SQLAlchemy database session.

    Returns:
        database.User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Query the database to find the user by ID obtained from the token
    user = db.query(database.User).filter(database.User.id == current_user.id).first()
    if user is None:
        raise credentials_exception  # Raise an error if user does not exist

    return user  # Return the user profile
