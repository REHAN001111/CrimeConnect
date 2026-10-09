from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    DateField,
    TimeField,
    BooleanField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Regexp,
    Length,
    EqualTo,
    Optional,
    ValidationError
)
from models import User, Complaint

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf', 'txt', 'docx']
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class RegistrationForm(FlaskForm):
    """User registration form with email uniqueness check and strong validation."""
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(message="Please enter your full name."), Length(min=2, max=120)]
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Please enter your email."),
            Regexp(EMAIL_REGEX, message="Invalid email format.")
        ]
    )
    phone = StringField(
        'Phone Number (Optional)',
        validators=[Optional(), Length(min=7, max=20, message="Enter a valid phone number (7-20 digits).")]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=6, message="Password must be at least 6 characters.")
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """Ensure no duplicate email addresses."""
        email_clean = field.data.strip().lower()
        if User.query.filter_by(email=email_clean).first():
            raise ValidationError('This email address is already registered. Please log in or use another email.')


class LoginForm(FlaskForm):
    """Authentication form for existing users and administrators."""
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Please enter your email."),
            Regexp(EMAIL_REGEX, message="Invalid email address.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Please enter your password.")]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ComplaintForm(FlaskForm):
    """Incident report filing form with validation and optional attachment."""
    category = SelectField(
        'Complaint Category',
        choices=[(c, c) for c in Complaint.CATEGORIES],
        validators=[DataRequired(message="Please select a complaint category.")]
    )
    title = StringField(
        'Incident Title',
        validators=[
            DataRequired(message="Please provide a concise incident title."),
            Length(min=5, max=150, message="Title must be between 5 and 150 characters.")
        ]
    )
    incident_date = DateField(
        'Incident Date',
        validators=[DataRequired(message="Please specify the date of the incident.")]
    )
    incident_time = TimeField(
        'Approximate Time (Optional)',
        validators=[Optional()]
    )
    incident_location = StringField(
        'Incident Location / Area',
        validators=[
            DataRequired(message="Please specify the location or online platform."),
            Length(min=3, max=255, message="Location must be between 3 and 255 characters.")
        ]
    )
    description = TextAreaField(
        'Detailed Description',
        validators=[
            DataRequired(message="Please provide a detailed description of what happened."),
            Length(min=20, message="Description must be at least 20 characters for clear reporting.")
        ]
    )
    witness_information = TextAreaField(
        'Witness Details (Optional)',
        validators=[Optional(), Length(max=500)]
    )
    attachment = FileField(
        'Supporting Document / Evidence (Optional, max 5MB)',
        validators=[
            Optional(),
            FileAllowed(ALLOWED_EXTENSIONS, f"Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}")
        ]
    )
    accuracy_confirmation = BooleanField(
        'I confirm that this report contains factual information to the best of my knowledge for this academic demonstration.',
        validators=[DataRequired(message="You must acknowledge the accuracy declaration.")]
    )
    submit = SubmitField('Submit Complaint')


class ComplaintTrackingForm(FlaskForm):
    """Form to query status by reference number and verifying email."""
    reference_number = StringField(
        'Complaint Reference Number',
        validators=[DataRequired(message="Enter the reference number (e.g., CR-20261009-ABC12).")]
    )
    verification_email = StringField(
        'Complainant Email Address',
        validators=[
            DataRequired(message="Enter the registered email address to verify authorization."),
            Regexp(EMAIL_REGEX, message="Invalid email address.")
        ]
    )
    submit = SubmitField('Track Status')


class StatusUpdateForm(FlaskForm):
    """Admin form to transition complaint workflow status and leave public remarks."""
    status = SelectField(
        'Update Status',
        choices=[(s, s) for s in Complaint.STATUSES],
        validators=[DataRequired()]
    )
    public_remarks = TextAreaField(
        'Public Remarks for Complainant',
        validators=[Optional(), Length(max=1000)]
    )
    submit = SubmitField('Update Complaint Status')


class AdminNoteForm(FlaskForm):
    """Admin form to record internal confidential investigation notes."""
    note = TextAreaField(
        'Internal Administrative Note (Staff Only)',
        validators=[
            DataRequired(message="Note text cannot be empty."),
            Length(min=3, max=2000)
        ]
    )
    submit = SubmitField('Save Internal Note')
