from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, schemas, utils

# Initialize the router
router = APIRouter()


@router.post(
    "/", response_model=schemas.DailyLogResponse, status_code=status.HTTP_201_CREATED
)
def create_daily_log(
    log: schemas.DailyLogCreate,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> database.DailyLog:
    """
    Create a daily log entry for a specific challenge.

    Args:
        log (schemas.DailyLogCreate): Data needed to create a daily log entry.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.DailyLogResponse: Details of the created daily log entry.
    """
    # Check if the log for the specific date and challenge already exists
    existing_log = (
        db.query(database.DailyLog)
        .filter(
            database.DailyLog.challenge_id == log.challenge_id,
            database.DailyLog.log_date == log.log_date,
        )
        .first()
    )

    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A log entry for this date already exists",
        )

    new_log = database.DailyLog(
        challenge_id=log.challenge_id, log_date=log.log_date, completed=log.completed
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.get("/{challenge_id}", response_model=List[schemas.DailyLogResponse])
def get_logs_by_challenge(
    challenge_id: int,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> List[database.DailyLog]:
    """
    Retrieve all daily log entries for a specific challenge, ensuring that the
    challenge belongs to the authenticated user.

    Args:
        challenge_id (int): Unique identifier of the challenge.
        current_user (schemas.TokenData): The authenticated user.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        List[schemas.DailyLogResponse]: A list of daily log entries for the specified challenge.

    Raises:
        HTTPException: If the challenge does not exist or does not belong to the user.
    """
    # Check if the challenge exists and belongs to the current user
    challenge = (
        db.query(database.Challenge)
        .filter(
            database.Challenge.id == challenge_id,
            database.Challenge.user_id == current_user.id,
        )
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access logs for this challenge.",
        )

    # Retrieve logs for the challenge if the user is authorized
    logs = (
        db.query(database.DailyLog)
        .filter(database.DailyLog.challenge_id == challenge_id)
        .all()
    )
    return logs


@router.put("/{log_id}", response_model=schemas.DailyLogResponse)
def update_daily_log(
    log_id: int,
    log_update: schemas.DailyLogUpdate,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> database.DailyLog:
    """
    Update an existing daily log entry if the user is the owner of the associated challenge.

    Args:
        log_id (int): Unique identifier of the log entry to update.
        log_update (schemas.DailyLogUpdate): Data to update the log entry.
        current_user (schemas.TokenData): The authenticated user.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.DailyLogResponse: Updated daily log entry.

    Raises:
        HTTPException: If the daily log entry is not found or the user is not authorized.
    """
    # Retrieve the log entry and ensure it exists
    log_entry = (
        db.query(database.DailyLog).filter(database.DailyLog.id == log_id).first()
    )
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found"
        )

    # Verify ownership by checking if the challenge belongs to the authenticated user
    challenge = (
        db.query(database.Challenge)
        .filter(
            database.Challenge.id == log_entry.challenge_id,
            database.Challenge.user_id == current_user.id,
        )
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this log entry",
        )

    # Proceed to update the log entry if ownership is confirmed
    log_entry.completed = log_update.completed
    db.commit()
    db.refresh(log_entry)

    return log_entry


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_log(
    log_id: int,
    current_user: schemas.TokenData = Depends(utils.verify_token),
    db: Session = Depends(database.get_db),
) -> None:
    """
    Delete a daily log entry by its ID if the user is the owner of the associated challenge.

    Args:
        log_id (int): Unique identifier of the log entry to delete.
        current_user (schemas.TokenData): The authenticated user.
        db (Session, optional): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the daily log entry is not found or the user is not authorized.
    """
    # Retrieve the log entry and ensure it exists
    log_entry = (
        db.query(database.DailyLog).filter(database.DailyLog.id == log_id).first()
    )
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found"
        )

    # Verify ownership by checking if the challenge belongs to the authenticated user
    challenge = (
        db.query(database.Challenge)
        .filter(
            database.Challenge.id == log_entry.challenge_id,
            database.Challenge.user_id == current_user.id,
        )
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this log entry",
        )

    # Proceed to delete the log entry if ownership is confirmed
    db.delete(log_entry)
    db.commit()
    return None
