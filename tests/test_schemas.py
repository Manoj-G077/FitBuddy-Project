from app.schemas import FeedbackRequest, UserInput

def test_user_input():
    data = UserInput(
        username="Test User",
        user_id="test_01",
        age=25,
        weight=70,
        goal="general_wellness",
        intensity="medium",
    )
    assert data.username == "Test User"

def test_feedback_limit():
    data = FeedbackRequest(user_id="test_01", feedback="Add more recovery.")
    assert data.user_id == "test_01"
