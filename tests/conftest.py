"""pytest fixtures for usage with test cases via dependency injection

Example from:
    https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py
"""

from tests.fixtures.environment import EnvironmentFixture
from c8y_api.app import CumulocityApi
from c8y_api.model.inventory import Fragment, ManagedObject
import pytest
from cumulocity_flexy_integration.main import create_app


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def test_c8y():
    """Test c8y client fixture
    """
    c8y = CumulocityApi()
    yield c8y


@pytest.fixture(scope='module')
def test_environment(test_c8y):
    """Test flexy integration environment fixture to allow individual tests to create their own test managed objects
    """
    # gateway = EnvironmentFixture(test_c8y)
    # yield gateway
    # gateway.cleanup()


@pytest.fixture(scope='module')
def test_flexy(test_c8y):
    """Test 
    """
    # environment = EnvironmentFixture(test_c8y)
    # c_mo = environment.create_gateway('test_gateway')

    # yield c_mo

    # # Cleanup
    # c_mo.delete()
