"""
Functional tests for the version endpoint
"""
import json

from flask.testing import FlaskClient


def test_version(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/version' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/version')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'version' in data
