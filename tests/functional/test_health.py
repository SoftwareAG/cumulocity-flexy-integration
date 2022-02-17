"""
Functional tests for the health endpoint
"""
import json

from flask.testing import FlaskClient


def test_health(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/health' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'UP'
