from datetime import datetime, timezone
import secrets
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

def get_utc_now():
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    """User account model for both citizens and administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)

    # Relationships
    complaints = db.relationship('Complaint', backref='complainant', lazy=True, cascade='all, delete-orphan')
    admin_notes = db.relationship('AdminNote', backref='author', lazy=True)
    history_entries = db.relationship('ComplaintHistory', backref='changer', lazy=True)

    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify stored password against provided plaintext."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if user has administrative privileges."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


class Complaint(db.Model):
    """Complaint filing model representing citizen incident reports."""
    __tablename__ = 'complaints'

    # Valid categories
    CATEGORIES = [
        'Theft',
        'Cybercrime',
        'Fraud',
        'Harassment',
        'Vandalism',
        'Missing Property',
        'Other'
    ]

    # Valid workflow statuses
    STATUS_SUBMITTED = 'Submitted'
    STATUS_UNDER_REVIEW = 'Under Review'
    STATUS_INFO_REQUESTED = 'Additional Information Requested'
    STATUS_RESOLVED = 'Resolved'
    STATUS_CLOSED = 'Closed'

    STATUSES = [
        STATUS_SUBMITTED,
        STATUS_UNDER_REVIEW,
        STATUS_INFO_REQUESTED,
        STATUS_RESOLVED,
        STATUS_CLOSED
    ]

    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_date = db.Column(db.Date, nullable=False)
    incident_time = db.Column(db.Time, nullable=True)
    incident_location = db.Column(db.String(255), nullable=False)
    witness_information = db.Column(db.Text, nullable=True)
    attachment_filename = db.Column(db.String(255), nullable=True)
    attachment_original_name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Submitted', nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    history = db.relationship(
        'ComplaintHistory',
        backref='complaint',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='ComplaintHistory.created_at.desc()'
    )
    admin_notes = db.relationship(
        'AdminNote',
        backref='complaint',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='AdminNote.created_at.desc()'
    )

    @staticmethod
    def generate_reference_number():
        """
        Generate a unique reference number formatted as:
        CR-YYYYMMDD-XXXXX (where XXXXX is a 5-character uppercase hex token)
        """
        date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
        while True:
            random_hex = secrets.token_hex(3)[:5].upper()
            candidate = f"CR-{date_str}-{random_hex}"
            if not Complaint.query.filter_by(reference_number=candidate).first():
                return candidate

    @property
    def status_badge_class(self):
        """Return CSS class for badge color coding."""
        mapping = {
            self.STATUS_SUBMITTED: 'badge-submitted',
            self.STATUS_UNDER_REVIEW: 'badge-review',
            self.STATUS_INFO_REQUESTED: 'badge-info-requested',
            self.STATUS_RESOLVED: 'badge-resolved',
            self.STATUS_CLOSED: 'badge-closed'
        }
        return mapping.get(self.status, 'badge-secondary')

    def __repr__(self):
        return f'<Complaint {self.reference_number}: {self.title}>'


class ComplaintHistory(db.Model):
    """Audit log tracking all status transitions and public remarks."""
    __tablename__ = 'complaint_history'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    public_remarks = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)

    def __repr__(self):
        return f'<ComplaintHistory {self.complaint_id}: {self.previous_status} -> {self.new_status}>'


class AdminNote(db.Model):
    """Internal investigation notes visible exclusively to administrators."""
    __tablename__ = 'admin_notes'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)

    def __repr__(self):
        return f'<AdminNote {self.id} for Complaint {self.complaint_id}>'
