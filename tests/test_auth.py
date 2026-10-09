import pytest
from models import User
from extensions import db

def test_user_registration_success(client, app):
    """Test standard citizen registration with valid credentials."""
    response = client.post('/register', data={
        'full_name': 'Sarah Connor',
        'email': 'sarah@test.local',
        'phone': '555-9988',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account created successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='sarah@test.local').first()
        assert user is not None
        assert user.full_name == 'Sarah Connor'
        assert user.role == 'user'
        assert user.check_password('SecurePassword123') is True
        assert user.password_hash != 'SecurePassword123'  # Verify hashed

def test_duplicate_email_registration_fails(client):
    """Ensure duplicate emails cannot register."""
    response = client.post('/register', data={
        'full_name': 'Duplicate Person',
        'email': 'citizen@test.local',  # Already exists from fixture
        'phone': '555-1234',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'already registered' in response.data

def test_password_confirmation_mismatch(client):
    """Ensure mismatched passwords prevent account creation."""
    response = client.post('/register', data={
        'full_name': 'Mismatch Test',
        'email': 'mismatch@test.local',
        'password': 'Password123',
        'confirm_password': 'DifferentPassword456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Passwords must match' in response.data

def test_user_login_success(client):
    """Test successful authentication with valid credentials."""
    response = client.post('/login', data={
        'email': 'citizen@test.local',
        'password': 'CitizenPass123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back, Test Citizen' in response.data

def test_user_login_invalid_password(client):
    """Test authentication failure on invalid password."""
    response = client.post('/login', data={
        'email': 'citizen@test.local',
        'password': 'WrongPassword999'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_user_logout(auth_client):
    """Test user session termination."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out safely' in response.data
