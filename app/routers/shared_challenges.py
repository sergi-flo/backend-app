from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import database, schemas, utils

# Initialize the router
router = APIRouter()


@router.post(
    "/",
    response_model=schemas.SharedChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def share_challenge(
    shared_challenge: schemas.SharedChallengeCreate,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> database.SharedChallenge:
    """
    Share a challenge with another user.

    Args:
        shared_challenge (schemas.SharedChallengeCreate): Data needed to share a challenge.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.SharedChallengeResponse: Details of the shared challenge.
    """
    # Assuming `challenge_id` and `shared_user_id` are obtained from the request
    challenge = (
        db.query(database.Challenge)
        .filter(database.Challenge.id == shared_challenge.challenge_id)
        .first()
    )
    shared_user = (
        db.query(database.User)
        .filter(database.User.id == shared_challenge.shared_user_id)
        .first()
    )

    if not challenge or not shared_user:
        raise HTTPException(status_code=404, detail="Challenge or User not found")

    new_shared_challenge = database.SharedChallenge(
        challenge=challenge,
        shared_user=shared_user,
        shared_at=datetime.now(),
    )
    db.add(new_shared_challenge)
    db.commit()
    db.refresh(new_shared_challenge)

    return new_shared_challenge


@router.get("/user", response_model=List[schemas.SharedChallengeResponse])
def get_shared_challenges(
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> List[database.SharedChallenge]:
    """
    Retrieve all shared challenges for a specific user.

    Args:
        user_id (int): Unique identifier of the user.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        List[schemas.SharedChallengeResponse]: A list of challenges shared with the specified user.
    """

    shared_challenges = (
        db.query(database.SharedChallenge)
        .options(joinedload(database.SharedChallenge.challenge))
        .filter(database.SharedChallenge.shared_user_id == current_user.id)
        .all()
    )

    if not shared_challenges:
        return []

    # Convert database models to the response schema
    response_data = []
    for shared_challenge in shared_challenges:
        challenge = shared_challenge.challenge
        response_data.append(
            schemas.SharedChallengeResponse(
                id=shared_challenge.id,
                challenge_id=challenge.id,
                name=challenge.name,
                description=challenge.description,
                started_at=challenge.started_at,
                completed_at=challenge.completed_at,
                shared_at=shared_challenge.shared_at,
                shared_by=shared_challenge.challenge.user.username,
            )
        )
    return response_data


@router.delete("/id_{shared_challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shared_challenge(
    shared_challenge_id: int,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> None:
    """
    Delete a shared challenge entry by its ID if the user is the owner of the original challenge.

    Args:
        shared_challenge_id (int): Unique identifier of the shared challenge entry to delete.
        current_user (schemas.TokenData): The authenticated user.
        db (Session, optional): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the shared challenge entry is not found or the user is not authorized.
    """
    # Retrieve the shared challenge entry and ensure it exists
    shared_challenge = (
        db.query(database.SharedChallenge)
        .filter(database.SharedChallenge.id == shared_challenge_id)
        .first()
    )
    if not shared_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shared challenge not found"
        )

    # Verify ownership by checking if the original challenge belongs to the authenticated user
    challenge = (
        db.query(database.Challenge)
        .filter(
            database.Challenge.id == shared_challenge.challenge_id,
            database.Challenge.user_id == current_user.id,
        )
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this shared challenge",
        )

    # Proceed to delete the shared challenge entry if ownership is confirmed
    db.delete(shared_challenge)
    db.commit()
    return None
