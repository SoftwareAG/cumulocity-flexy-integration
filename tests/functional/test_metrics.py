"""
Functional tests for the metrics endpoint
"""

from flask.testing import FlaskClient


def test_metrics(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/metrics' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/metrics')
    assert response.status_code == 200
    assert response.data
