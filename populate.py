import requests

# Base URL of your API
BASE_URL = "http://localhost:8000/api/v1"

# User credentials
user1 = {"username": "user1", "password": "password1", "email": "user1@example.com"}

user2 = {"username": "user2", "password": "password2", "email": "user2@example.com"}


# Register users
def register_user(user_data):
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Registered {user_data['username']}")
    return response.json()


# Log in and obtain access token
def login_user(username, password, email):
    response = requests.post(
        f"{BASE_URL}/users/token",
        json={"username": username, "password": password, "email": email},
    )
    token = response.json()["access_token"]
    print(f"Logged in {username}")
    return token


# Add a challenge for a user
def create_challenge(token, name, description):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "description": description}
    response = requests.post(f"{BASE_URL}/challenges/", json=data, headers=headers)
    print(f"Challenge '{name}' created")
    return response.json()


# Create daily log entries
def create_daily_log(token, challenge_id, log_date, completed):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"challenge_id": challenge_id, "log_date": log_date, "completed": completed}
    response = requests.post(f"{BASE_URL}/daily-logs/", json=data, headers=headers)
    print(f"Daily log for challenge {challenge_id} on {log_date} created")
    return response.json()


# Share a challenge with another user
def share_challenge(token, challenge_id, shared_user_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"challenge_id": challenge_id, "shared_user_id": shared_user_id}
    response = requests.post(
        f"{BASE_URL}/shared-challenges/", json=data, headers=headers
    )
    print(f"Challenge {challenge_id} shared with user {shared_user_id}")
    return response.json()


# Populate database
def populate():
    response = requests.get("http://localhost:8000/")
    print(response.text)
    input("Press Enter to continue...")

    # Register users
    user1_data = register_user(user1)
    user2_data = register_user(user2)
    input("Press Enter to continue...")

    # Log in users
    token1 = login_user(user1["username"], user1["password"], user1["email"])
    token2 = login_user(user2["username"], user2["password"], user2["email"])
    input("Press Enter to continue...")

    # Create challenges for user 1
    challenge1_user1 = create_challenge(
        token1, "Quit Smoking", "Challenge to quit smoking for a month."
    )
    challenge2_user1 = create_challenge(
        token1, "Daily Exercise", "Challenge to exercise every day."
    )
    input("Press Enter to continue...")

    # Create challenges for user 2
    challenge1_user2 = create_challenge(
        token2, "Read Books", "Challenge to read a book per week."
    )
    challenge2_user2 = create_challenge(
        token2, "Healthy Eating", "Challenge to eat healthy meals daily."
    )
    input("Press Enter to continue...")

    challeges1 = requests.get(
        f"{BASE_URL}/challenges/all_challenges",
        headers={"Authorization": f"Bearer {token1}"},
    )
    print(challeges1.json())
    challeges2 = requests.get(
        f"{BASE_URL}/challenges/all_challenges",
        headers={"Authorization": f"Bearer {token2}"},
    )
    print(challeges2.json())
    input("Press Enter to continue...")

    # Add daily logs to challenges for user 1
    create_daily_log(token1, challenge1_user1["id"], "2024-11-01", True)
    create_daily_log(token1, challenge1_user1["id"], "2024-11-02", False)
    create_daily_log(token1, challenge2_user1["id"], "2024-11-01", True)
    create_daily_log(token1, challenge2_user1["id"], "2024-11-02", True)
    input("Press Enter to continue...")

    # Add daily logs to challenges for user 2
    create_daily_log(token2, challenge1_user2["id"], "2024-11-01", True)
    create_daily_log(token2, challenge2_user2["id"], "2024-11-01", False)
    input("Press Enter to continue...")

    # Share one of user 1's challenges with user 2
    share_challenge(token1, challenge1_user1["id"], user2_data["id"])
    input("Press Enter to continue...")


# Run the script
populate()
