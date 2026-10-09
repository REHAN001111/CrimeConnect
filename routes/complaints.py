import os
import uuid
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    send_from_directory,
    abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Complaint, ComplaintHistory
from forms import ComplaintForm, ComplaintTrackingForm

complaints_bp = Blueprint('complaints', __name__)

def save_attachment(file_storage):
    """
    Safely store uploaded document with randomized UUID prefix 
    to prevent path traversal and file collision.
    """
    if not file_storage or file_storage.filename == '':
        return None, None

    original_filename = secure_filename(file_storage.filename)
    extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
    
    # Generate unique stored filename
    stored_filename = f"{uuid.uuid4().hex}_{int(os.times().elapsed)}.{extension}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, stored_filename)
    file_storage.save(file_path)
    return stored_filename, original_filename

@complaints_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report_complaint():
    """Register a new complaint and generate an instant tracking reference number."""
    form = ComplaintForm()
    if form.validate_on_submit():
        stored_file, orig_file = None, None
        if form.attachment.data:
            stored_file, orig_file = save_attachment(form.attachment.data)

        # Generate unique reference code
        ref_number = Complaint.generate_reference_number()

        complaint = Complaint(
            reference_number=ref_number,
            user_id=current_user.id,
            category=form.category.data,
            title=form.title.data.strip(),
            incident_date=form.incident_date.data,
            incident_time=form.incident_time.data,
            incident_location=form.incident_location.data.strip(),
            description=form.description.data.strip(),
            witness_information=form.witness_information.data.strip() if form.witness_information.data else None,
            attachment_filename=stored_file,
            attachment_original_name=orig_file,
            status=Complaint.STATUS_SUBMITTED
        )

        db.session.add(complaint)
        db.session.flush()  # Obtain complaint.id

        # Record initial status in history timeline
        initial_history = ComplaintHistory(
            complaint_id=complaint.id,
            previous_status='None',
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks='Complaint successfully filed by complainant and logged into CrimeConnect repository.',
            changed_by=current_user.id
        )
        db.session.add(initial_history)
        db.session.commit()

        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('complaints.submission_success', ref=ref_number))

    return render_template('report_complaint.html', form=form)

@complaints_bp.route('/submission-success/<ref>')
@login_required
def submission_success(ref):
    """Confirmation page with unique complaint tracking number."""
    complaint = Complaint.query.filter_by(reference_number=ref).first_or_404()
    if complaint.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('complaint_success.html', complaint=complaint)

@complaints_bp.route('/dashboard')
@login_required
def dashboard():
    """User Dashboard listing personal complaints, status summary, search and filter."""
    query = Complaint.query.filter_by(user_id=current_user.id)

    # Search filter
    search_keyword = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    if search_keyword:
        query = query.filter(
            (Complaint.title.ilike(f'%{search_keyword}%')) |
            (Complaint.reference_number.ilike(f'%{search_keyword}%')) |
            (Complaint.incident_location.ilike(f'%{search_keyword}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    complaints_list = query.order_by(Complaint.created_at.desc()).all()

    # Dynamic metrics
    total_count = Complaint.query.filter_by(user_id=current_user.id).count()
    under_review_count = Complaint.query.filter_by(
        user_id=current_user.id,
        status=Complaint.STATUS_UNDER_REVIEW
    ).count()
    resolved_count = Complaint.query.filter_by(
        user_id=current_user.id,
        status=Complaint.STATUS_RESOLVED
    ).count()

    return render_template(
        'user_dashboard.html',
        complaints=complaints_list,
        total_count=total_count,
        under_review_count=under_review_count,
        resolved_count=resolved_count,
        categories=Complaint.CATEGORIES,
        statuses=Complaint.STATUSES,
        search_keyword=search_keyword,
        status_filter=status_filter,
        category_filter=category_filter
    )

@complaints_bp.route('/view/<int:complaint_id>')
@login_required
def view_complaint(complaint_id):
    """Detailed view of an individual complaint with full audit timeline and public remarks."""
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    return render_template('complaint_details.html', complaint=complaint)

@complaints_bp.route('/track', methods=['GET', 'POST'])
def track_complaint():
    """
    Public tracking portal with authorization verification.
    Requires Reference Number + Complainant's Registered Email to safeguard privacy.
    """
    form = ComplaintTrackingForm()
    complaint = None
    error_message = None

    if form.validate_on_submit():
        ref = form.reference_number.data.strip()
        email = form.verification_email.data.strip().lower()

        candidate = Complaint.query.filter_by(reference_number=ref).first()
        if candidate and candidate.complainant.email.lower() == email:
            complaint = candidate
        else:
            error_message = "No matching complaint found for the provided reference number and verification email combination."

    return render_template('track_complaint.html', form=form, complaint=complaint, error_message=error_message)

@complaints_bp.route('/attachment/<int:complaint_id>')
@login_required
def download_attachment(complaint_id):
    """
    Authorized evidence file download. Only accessible by the complaint owner or administrators.
    """
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if not complaint.attachment_filename:
        flash('No file attached to this complaint.', 'warning')
        return redirect(url_for('complaints.view_complaint', complaint_id=complaint.id))

    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(
        upload_dir,
        complaint.attachment_filename,
        download_name=complaint.attachment_original_name or 'complaint_evidence',
        as_attachment=True
    )
