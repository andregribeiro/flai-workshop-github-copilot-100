"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join the school soccer team and compete against other schools",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "william@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges at regional competitions",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Drama Club" in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        soccer_team = data["Soccer Team"]
        
        assert "description" in soccer_team
        assert "schedule" in soccer_team
        assert "max_participants" in soccer_team
        assert "participants" in soccer_team
        assert isinstance(soccer_team["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Soccer Team"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_registered_student(self, client):
        """Test signup for a student who is already registered"""
        # james@mergington.edu is already in Soccer Team
        response = client.post(
            "/activities/Soccer Team/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        # First student
        response1 = client.post(
            "/activities/Drama Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second student
        response2 = client.post(
            "/activities/Drama Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both students are in the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Drama Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity(self, client):
        """Test successful unregistration from an activity"""
        # james@mergington.edu is registered for Soccer Team
        response = client.delete(
            "/activities/Soccer Team/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered james@mergington.edu from Soccer Team"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "james@mergington.edu" not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client):
        """Test unregistration for a student who is not registered"""
        response = client.delete(
            "/activities/Soccer Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_and_register_again(self, client):
        """Test that a student can unregister and then register again"""
        # Unregister james@mergington.edu
        response1 = client.delete(
            "/activities/Soccer Team/unregister?email=james@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Register again
        response2 = client.post(
            "/activities/Soccer Team/signup?email=james@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify student is back in the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "james@mergington.edu" in activities_data["Soccer Team"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_student_signup_and_unregister_workflow(self, client):
        """Test a complete workflow of signing up and unregistering"""
        email = "testuser@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()["Chess Club"]["participants"]
        assert email not in initial_participants
        
        # Sign up
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        after_signup_participants = after_signup.json()["Chess Club"]["participants"]
        assert email in after_signup_participants
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        after_unregister = client.get("/activities")
        after_unregister_participants = after_unregister.json()["Chess Club"]["participants"]
        assert email not in after_unregister_participants
