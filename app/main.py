from fastapi import FastAPI

from app.config import settings
from app.routers import challenges, daily_logs, shared_challenges, users

# Initialize the FastAPI application
app = FastAPI(
    title="Daily Task Tracker API",
    description="An API for managing daily progress on personal challenges",
    version="1.0.0",
)


# Include API routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["Challenges"])
app.include_router(daily_logs.router, prefix="/api/v1/daily-logs", tags=["Daily Logs"])
app.include_router(
    shared_challenges.router,
    prefix="/api/v1/shared-challenges",
    tags=["Shared Challenges"],
)


@app.get("/")
def read_root():
    """
    Root endpoint to verify API is up and running.

    Returns:
        dict: A message confirming API status.
    """
    print("HOT RELOAD", settings.DATABASE_URL)
    return {"message": "Welcome to the Daily Task Tracker API!"}
