from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, schemas
from app.schemas import TokenData
from app.utils import verify_token

# Initialize the router
router = APIRouter()


@router.post(
    "/", response_model=schemas.ChallengeResponse, status_code=status.HTTP_201_CREATED
)
def create_challenge(
    challenge: schemas.ChallengeCreate,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(database.get_db),
) -> database.Challenge:
    """
    Create a new challenge for a user.

    Args:
        challenge (schemas.ChallengeCreate): Data needed to create a challenge.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.ChallengeResponse: Details of the newly created challenge.
    """
    # Check if user with the same username or email already exists
    existing_challenge = (
        db.query(database.Challenge)
        .filter(
            (database.Challenge.user_id == current_user.id),
            (database.Challenge.name == challenge.name),
        )
        .first()
    )

    if existing_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A challenge with this name already exists for the user.",
        )

    # Create the new challenge
    new_challenge = database.Challenge(
        user_id=current_user.id,
        name=challenge.name,
        description=challenge.description,
        started_at=datetime.now(),
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

    return new_challenge


@router.get("/id_{challenge_id}", response_model=schemas.ChallengeResponse)
def get_challenge(
    challenge_id: int,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(database.get_db),
) -> database.Challenge:
    """
    Retrieve details of a specific challenge by ID.

    Args:
        challenge_id (int): Unique identifier of the challenge.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.ChallengeResponse: Details of the challenge for the specified ID.

    Raises:
        HTTPException: If the challenge with the specified ID is not found.
    """
    challenge = (
        db.query(database.Challenge)
        .filter(database.Challenge.id == challenge_id)
        .first()
    )
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found"
        )
    return challenge


@router.get("/all_challenges", response_model=List[schemas.ChallengeResponse])
def get_challenges_by_user(
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(database.get_db),
) -> List[database.Challenge]:
    """
    Retrieve all challenges for a specific user by their user ID.

    Args:
        user_id (int): Unique identifier of the user.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        List[schemas.ChallengeResponse]: A list of challenges belonging to the specified user.
    """
    challenges = (
        db.query(database.Challenge)
        .filter(database.Challenge.user_id == current_user.id)
        .all()
    )
    return challenges
