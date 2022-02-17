import pytest
from ..app import create_app
from ..app import db


# the returned list can be used anywhere in the tests/ directory
# and would be referenced directly as a list from anywhere with name "my_list" (same as the function name)
@pytest.fixture(scope='module')
def my_list():
    return [3, 4, 7, 8]

# allows a new app creation in any test unit and does not require creation or removal of info from the database
@pytest.fixture(scope='module')
def new_app():
    # setup
    app = create_app('testing')
    assert 'data-test.sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    # testing begins
    yield test_client

    # teardown
    db.session.remove()
    db.drop_all()
    ctx.pop()