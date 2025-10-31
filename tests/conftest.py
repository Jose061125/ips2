import pytest
from app import create_app
from app.models import db, User
from flask_login import login_user

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
        'LOGIN_DISABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='testuser', role='admin')  # Default to admin for tests
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_client(client, test_user):
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    return client

class AuthActions:
    """Helper class for authentication actions in tests"""
    def __init__(self, client, app):
        self._client = client
        self._app = app
    
    def login(self, username='testuser', password='testpass'):
        with self._app.app_context():
            return self._client.post('/auth/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
    
    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)

@pytest.fixture
def auth(client, app):
    return AuthActions(client, app)
