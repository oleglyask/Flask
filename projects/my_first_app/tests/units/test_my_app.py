
from flask import current_app
from ...app import db
from ...app.models import User
from ...app import create_app

def test_app_creation():
    app = create_app('testing')
    assert app

def test_current_app():
    app = create_app('testing')
    app.app_context().push()
    assert current_app
    assert current_app.config['TESTING']

def test_database_insert():
    app = create_app('testing')
    assert app.config['TESTING']
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    # ensure test database configured
    assert 'data-test.sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    app.app_context().push()
    # create all tables if not created
    db.create_all()

    u = User(username='john')
    db.session.add(u)
    db.session.commit()

    # IMPORTANT clear database for future tests
    db.session.remove()
    db.drop_all()

# This is what the above test should look like using fixtures
# def test_database_insert(new_app):
#     u = User(email='john@example.com', username='john')
#     db.session.add(u)
#     db.session.commit()
