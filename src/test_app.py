"""
Tests for the High School Management System API

These tests validate the functionality of the school website's backend API.
"""

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_root_redirects_to_index():
    """Test that root URL redirects to the static index page"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test that activities endpoint returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all expected activities are present
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Verify structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club


def test_activities_have_required_fields():
    """Test that each activity has all required fields"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for activity_name, activity_data in data.items():
        for field in required_fields:
            assert field in activity_data, f"{activity_name} missing field: {field}"


def test_signup_for_existing_activity():
    """Test signing up for an existing activity"""
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_data = initial_response.json()
    initial_count = len(initial_data["Chess Club"]["participants"])
    
    # Sign up for Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    after_response = client.get("/activities")
    after_data = after_response.json()
    assert len(after_data["Chess Club"]["participants"]) == initial_count + 1
    assert "test@mergington.edu" in after_data["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity():
    """Test that signing up for a non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
