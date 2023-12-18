import pytest
from flask_server import app  # Import your Flask app instance


@pytest.fixture
def client():
    """Create a test client for the app."""
    return app.test_client()


def test_your_route_with_optional_argument(client):
    """Test the route with all three arguments provided."""
    response = client.get("/get_token_frame?source_type=vfgh&index=0&year=2022")

    assert response.status_code == 200
    assert "all good (judikatur)" == response.text


def test_your_route_without_optional_argument(client):
    """Test the route with only mandatory arguments."""
    response = client.get("/get_token_frame?source_type=PHG&index=0")

    assert response.status_code == 200
    assert "all good (bundesrecht)" == response.text



