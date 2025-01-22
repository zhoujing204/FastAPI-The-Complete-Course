from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'

def test_create_user():
    # Input data for the endpoint
    create_user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "password": "strongpassword",
        "phone_number": "1234567890"
    }

    # Send a POST request to the endpoint
    response = client.post("/auth/", json=create_user_data)

    # Assert endpoint response
    assert response.status_code == 201, f"Response: {response.content}"


    # Verify that the user was created in the database
    db = TestingSessionLocal()
    created_user = db.query(Users).filter(Users.username == create_user_data["username"]).first()
    assert created_user is not None
    assert created_user.email == create_user_data["email"]
    assert created_user.username == create_user_data["username"]
    assert created_user.first_name == create_user_data["first_name"]
    assert created_user.last_name == create_user_data["last_name"]
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

def test_login_for_access_token_success(test_user):
    """Test successful login and token generation."""
    # Input data for the login
    login_data = {
        "username": "codingwithrobytest",
        "password": "testpassword",
    }

    # Send a POST request to the /auth/token endpoint
    response = client.post(
        "/auth/token",
        data={"username": login_data["username"], "password": login_data["password"]},
    )

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

def test_login_for_access_token_invalid_credentials(test_user):
    """Test login with invalid credentials."""
    # Input data with incorrect password
    login_data = {
        "username": "codingwithrobytest",
        "password": "wrongpassword",
    }

    # Send a POST request to the /auth/token endpoint
    response = client.post(
        "/auth/token",
        data={"username": login_data["username"], "password": login_data["password"]},
    )

    # Assert the response
    assert response.status_code == 401
    response_data = response.json()
    assert response_data["detail"] == "Could not validate user."

def test_login_for_access_token_nonexistent_user():
    """Test login with a nonexistent username."""
    # Input data with a username that doesn't exist
    login_data = {
        "username": "nonexistentuser",
        "password": "testpassword",
    }

    # Send a POST request to the /auth/token endpoint
    response = client.post(
        "/auth/token",
        data={"username": login_data["username"], "password": login_data["password"]},
    )

    # Assert the response
    assert response.status_code == 401
    response_data = response.json()
    assert response_data["detail"] == "Could not validate user."