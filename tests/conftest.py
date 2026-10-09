import os
import sys

# Ensure project root is in python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from config import TestingConfig
from extensions import db
from models import User, Complaint

@pytest.fixture
def app():
    """Create and configure a clean testing application instance."""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create standard test admin
        test_admin = User(
            full_name="Test Administrator",
            email="admin@test.local",
            phone="555-0001",
            role="admin"
        )
        test_admin.set_password("AdminPass123")
        db.session.add(test_admin)

        # Create standard test citizen
        test_citizen = User(
            full_name="Test Citizen",
            email="citizen@test.local",
            phone="555-0002",
            role="user"
        )
        test_citizen.set_password("CitizenPass123")
        db.session.add(test_citizen)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the application."""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Test client pre-authenticated as the standard test citizen."""
    client.post('/login', data={
        'email': 'citizen@test.local',
        'password': 'CitizenPass123'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client):
    """Test client pre-authenticated as the standard administrator."""
    client.post('/login', data={
        'email': 'admin@test.local',
        'password': 'AdminPass123'
    }, follow_redirects=True)
    return client
