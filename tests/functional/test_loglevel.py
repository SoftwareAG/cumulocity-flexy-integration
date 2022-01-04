"""
Functional tests for the loglevel endpoint
"""
import json

from flask.testing import FlaskClient


def test_loglevel(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/loglevel' page is requested (POST)
    THEN check the response is valid and includes the new log level
    """
    response = test_client.post('/loglevel', json={'level': 'ERROR'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['level'] == 'ERROR'

    response = test_client.get('/loglevel')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['level'] == 'ERROR'


def test_invalid_loglevel(test_client: FlaskClient):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/loglevel' page is requested (POST) with an invalid log level
    THEN the status code should be set to 500 with json error message
    """
    response = test_client.post('/loglevel', json={'level': 'INVALID'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'code' in data
    assert 'error' in data
    assert 'message' in data
