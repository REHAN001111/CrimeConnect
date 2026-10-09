import io
import pytest
from datetime import date
from models import Complaint, User
from extensions import db

def test_complaint_submission_success(auth_client, app):
    """Test complaint creation and unique reference number assignment."""
    response = auth_client.post('/report', data={
        'category': 'Theft',
        'title': 'Stolen Bicycle from Library Stand',
        'incident_date': '2026-10-09',
        'incident_location': 'Central Library West Bike Stand',
        'description': 'A silver Giant road bike was locked at the stand and stolen between 2 PM and 5 PM.',
        'witness_information': 'Library guard saw suspicious person around 3 PM.',
        'accuracy_confirmation': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Complaint Successfully Logged' in response.data

    with app.app_context():
        complaint = Complaint.query.filter_by(title='Stolen Bicycle from Library Stand').first()
        assert complaint is not None
        assert complaint.reference_number.startswith('CR-')
        assert complaint.status == Complaint.STATUS_SUBMITTED
        assert len(complaint.history) == 1
        assert complaint.history[0].new_status == Complaint.STATUS_SUBMITTED

def test_complaint_submission_validation_errors(auth_client):
    """Test validation failure on short description and missing required fields."""
    response = auth_client.post('/report', data={
        'category': 'Theft',
        'title': 'Test',
        'incident_date': '2026-10-09',
        'incident_location': 'Loc',
        'description': 'Too short',  # Below 20 chars minimum
        'accuracy_confirmation': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Description must be at least 20 characters' in response.data

def test_user_complaint_isolation(client, app):
    """Ensure user B cannot view user A's private complaint details."""
    with app.app_context():
        citizen1 = User.query.filter_by(email='citizen@test.local').first()
        c = Complaint(
            reference_number="CR-20261009-TEST1",
            user_id=citizen1.id,
            category="Fraud",
            title="Private Incident Case",
            description="Detailed confidential fraud report description text here.",
            incident_date=date(2026, 10, 9),
            incident_location="Bank Branch",
            status=Complaint.STATUS_SUBMITTED
        )
        db.session.add(c)

        # Create another citizen
        citizen2 = User(
            full_name="Other Citizen",
            email="other@test.local",
            role="user"
        )
        citizen2.set_password("Pass123")
        db.session.add(citizen2)
        db.session.commit()
        complaint_id = c.id

    # Log in as other citizen
    client.post('/login', data={'email': 'other@test.local', 'password': 'Pass123'}, follow_redirects=True)

    # Attempt to access citizen 1's complaint
    response = client.get(f'/view/{complaint_id}')
    assert response.status_code == 403

def test_complaint_tracking_authorization(client, app):
    """Ensure complaint tracking requires reference number + complainant email."""
    with app.app_context():
        user = User.query.filter_by(email='citizen@test.local').first()
        c = Complaint(
            reference_number="CR-20261009-TRACK",
            user_id=user.id,
            category="Cybercrime",
            title="Trackable Cyber Incident",
            description="Detailed description of trackable cyber incident report.",
            incident_date=date(2026, 10, 9),
            incident_location="Online",
            status=Complaint.STATUS_SUBMITTED
        )
        db.session.add(c)
        db.session.commit()

    # Query with correct ref + correct email
    valid_res = client.post('/track', data={
        'reference_number': 'CR-20261009-TRACK',
        'verification_email': 'citizen@test.local'
    })
    assert valid_res.status_code == 200
    assert b'Trackable Cyber Incident' in valid_res.data
    assert b'Incident Case File' in valid_res.data

    # Query with correct ref + wrong email
    invalid_res = client.post('/track', data={
        'reference_number': 'CR-20261009-TRACK',
        'verification_email': 'stranger@test.local'
    })
    assert invalid_res.status_code == 200
    assert b'No matching complaint found' in invalid_res.data

def test_complaint_file_upload_allowed_type(auth_client, app):
    """Test file upload validation accepts allowed file type."""
    fake_file = (io.BytesIO(b"Dummy evidence file content"), "evidence.pdf")

    response = auth_client.post('/report', data={
        'category': 'Cybercrime',
        'title': 'Phishing Scam with PDF Screenshot',
        'incident_date': '2026-10-09',
        'incident_location': 'Student Portal',
        'description': 'Received phishing email with fake invoice attached.',
        'attachment': fake_file,
        'accuracy_confirmation': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Complaint Successfully Logged' in response.data

    with app.app_context():
        c = Complaint.query.filter_by(title='Phishing Scam with PDF Screenshot').first()
        assert c is not None
        assert c.attachment_original_name == 'evidence.pdf'
        assert c.attachment_filename is not None
