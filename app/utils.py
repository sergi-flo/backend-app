from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT access token.

    Args:
        data (dict): Data to include in the token payload.
        expires_delta (timedelta, optional): Expiration time delta for the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = (
        datetime.now() + expires_delta
        if expires_delta
        else datetime.now() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Verifies the JWT token passed in the Authorization header.

    Args:
        token (str): The JWT token extracted from the request header.

    Returns:
        TokenData: The data contained within the token (e.g., user ID).

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("id")
        username: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(id=user_id, username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
