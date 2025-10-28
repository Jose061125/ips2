import pytest
from flask import session
from app.models import User

def test_register_get(client):
    """Test the registration page loads correctly"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Registro' in response.data

def test_register_post(client):
    """Test user registration with valid password"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'password': 'TestPass123!',  # Meets password policy
        'password2': 'TestPass123!',
        'role': 'recepcionista'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for success message
    assert b'usuario registrado' in response.data.lower()
    
    # Verify user was created in database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.username == 'newuser'

def test_register_post_weak_password(client):
    """Test that registration fails with a weak password"""
    test_data = {
        'username': 'testuser',
        'password': 'weak',  # Intentionally weak password
        'password2': 'weak',
        'role': 'recepcionista'
    }
    
    response = client.post(
        '/auth/register', 
        data=test_data, 
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'password must be at least 8 characters' in response.data.lower()
    
    # Verify no user was created
    with client.application.app_context():
        user = User.query.filter_by(username=test_data['username']).first()
        assert user is None

@pytest.mark.parametrize("password,expected_error", [
    ("short", "at least 8 characters"),
    ("lowercase123!", "uppercase letter"),
    ("UPPERCASE123!", "lowercase letter"),
    ("NoNumbers!", "number"),
    ("NoSpecial123", "special character")
])
def test_password_policy_validations(client, password, expected_error):
    """Test different password policy validations"""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': password,
        'password2': password,
        'role': 'recepcionista'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert expected_error.encode() in response.data.lower()

def test_login_get(client):
    """Test login page loads correctly"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Iniciar' in response.data or b'Login' in response.data

def test_login_post(client, test_user):
    """Test login with correct credentials"""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'iniciado sesi' in response.data.lower()

def test_login_post_invalid_user(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    data = response.data.lower()
    # Aceptar mensaje en inglés o español (con/sin acento)
    assert (b'invalid' in data) or (b'usuario' in data)

def test_logout(client, test_user):
    """Test logout functionality"""
    # First login
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    
    # Then logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'cerrado sesi' in response.data.lower()
