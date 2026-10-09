import pytest
from datetime import date
from models import Complaint, User, ComplaintHistory, AdminNote
from extensions import db

def test_unauthorized_admin_access_rejected(auth_client):
    """Ensure regular citizen accounts are denied access to admin console."""
    response = auth_client.get('/admin/dashboard')
    assert response.status_code == 403

def test_admin_dashboard_access_granted(admin_client):
    """Ensure administrators can view the dashboard."""
    response = admin_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Incident Management Console' in response.data

def test_admin_status_update_and_audit_history(admin_client, app):
    """Test that admin can transition complaint status with remarks."""
    with app.app_context():
        citizen = User.query.filter_by(email='citizen@test.local').first()
        c = Complaint(
            reference_number="CR-20261009-ADMIN1",
            user_id=citizen.id,
            category="Theft",
            title="Theft Incident Under Investigation",
            description="Detailed report for admin workflow status testing.",
            incident_date=date(2026, 10, 9),
            incident_location="Main Quad",
            status=Complaint.STATUS_SUBMITTED
        )
        db.session.add(c)
        db.session.commit()
        complaint_id = c.id

    # Update status to Under Review with public remarks
    response = admin_client.post(f'/admin/complaint/{complaint_id}', data={
        'update_status': '1',
        'status': Complaint.STATUS_UNDER_REVIEW,
        'public_remarks': 'Assigned to Officer Martinez for area inspection.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'successfully changed to' in response.data

    with app.app_context():
        updated = Complaint.query.get(complaint_id)
        assert updated.status == Complaint.STATUS_UNDER_REVIEW
        
        # Check history entry was recorded
        latest_history = ComplaintHistory.query.filter_by(complaint_id=complaint_id).order_by(ComplaintHistory.created_at.desc()).first()
        assert latest_history is not None
        assert latest_history.new_status == Complaint.STATUS_UNDER_REVIEW
        assert 'Assigned to Officer Martinez' in latest_history.public_remarks

def test_admin_confidential_note_recording(admin_client, app):
    """Test that admin can record internal staff notes."""
    with app.app_context():
        citizen = User.query.filter_by(email='citizen@test.local').first()
        c = Complaint(
            reference_number="CR-20261009-NOTE1",
            user_id=citizen.id,
            category="Harassment",
            title="Harassment Case for Note Test",
            description="Testing internal note persistence in database.",
            incident_date=date(2026, 10, 9),
            incident_location="Hallway",
            status=Complaint.STATUS_SUBMITTED
        )
        db.session.add(c)
        db.session.commit()
        complaint_id = c.id

    response = admin_client.post(f'/admin/complaint/{complaint_id}', data={
        'add_note': '1',
        'note': 'Confidential IP trace result: matches dormitory subnet.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Internal administrative note recorded' in response.data

    with app.app_context():
        note = AdminNote.query.filter_by(complaint_id=complaint_id).first()
        assert note is not None
        assert 'matches dormitory subnet' in note.note

def test_admin_csv_export(admin_client):
    """Test that admin can export complaint records to CSV format."""
    response = admin_client.get('/admin/export-csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Reference Number,Title,Category,Status' in response.data
