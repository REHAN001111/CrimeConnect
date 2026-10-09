import csv
import io
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    Response,
    abort
)
from flask_login import login_required, current_user
from extensions import db
from models import Complaint, ComplaintHistory, AdminNote
from forms import StatusUpdateForm, AdminNoteForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator ensuring that only users with 'admin' role can access the endpoint."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Administrator control center with metrics, charts, and filterable table."""
    # Summary statistics
    total_count = Complaint.query.count()
    submitted_count = Complaint.query.filter_by(status=Complaint.STATUS_SUBMITTED).count()
    under_review_count = Complaint.query.filter_by(status=Complaint.STATUS_UNDER_REVIEW).count()
    info_requested_count = Complaint.query.filter_by(status=Complaint.STATUS_INFO_REQUESTED).count()
    resolved_count = Complaint.query.filter_by(status=Complaint.STATUS_RESOLVED).count()
    closed_count = Complaint.query.filter_by(status=Complaint.STATUS_CLOSED).count()

    # Query params for filtering
    search_keyword = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Complaint.query

    if search_keyword:
        query = query.filter(
            (Complaint.reference_number.ilike(f'%{search_keyword}%')) |
            (Complaint.title.ilike(f'%{search_keyword}%')) |
            (Complaint.incident_location.ilike(f'%{search_keyword}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    pagination = query.order_by(Complaint.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    complaints = pagination.items

    # Category counts for stats
    category_counts = {}
    for cat in Complaint.CATEGORIES:
        category_counts[cat] = Complaint.query.filter_by(category=cat).count()

    return render_template(
        'admin_dashboard.html',
        complaints=complaints,
        pagination=pagination,
        total_count=total_count,
        submitted_count=submitted_count,
        under_review_count=under_review_count,
        info_requested_count=info_requested_count,
        resolved_count=resolved_count,
        closed_count=closed_count,
        category_counts=category_counts,
        categories=Complaint.CATEGORIES,
        statuses=Complaint.STATUSES,
        search_keyword=search_keyword,
        status_filter=status_filter,
        category_filter=category_filter
    )

@admin_bp.route('/complaint/<int:complaint_id>', methods=['GET', 'POST'])
@admin_required
def complaint_detail(complaint_id):
    """Detailed view for administrators to review evidence, update status, and add notes."""
    complaint = Complaint.query.get_or_404(complaint_id)
    status_form = StatusUpdateForm(status=complaint.status)
    note_form = AdminNoteForm()

    if 'update_status' in request.form and status_form.validate_on_submit():
        new_status = status_form.status.data
        remarks = status_form.public_remarks.data.strip() if status_form.public_remarks.data else ''

        if new_status != complaint.status or remarks:
            prev_status = complaint.status
            complaint.status = new_status

            # Append to history audit trail
            history_entry = ComplaintHistory(
                complaint_id=complaint.id,
                previous_status=prev_status,
                new_status=new_status,
                public_remarks=remarks or f"Status updated to '{new_status}' by administrator.",
                changed_by=current_user.id
            )
            db.session.add(history_entry)
            db.session.commit()

            flash(f"Status for {complaint.reference_number} successfully changed to '{new_status}'.", 'success')
            return redirect(url_for('admin.complaint_detail', complaint_id=complaint.id))

    if 'add_note' in request.form and note_form.validate_on_submit():
        note_text = note_form.note.data.strip()
        internal_note = AdminNote(
            complaint_id=complaint.id,
            admin_id=current_user.id,
            note=note_text
        )
        db.session.add(internal_note)
        db.session.commit()

        flash('Internal administrative note recorded.', 'info')
        return redirect(url_for('admin.complaint_detail', complaint_id=complaint.id))

    return render_template(
        'admin_complaint_detail.html',
        complaint=complaint,
        status_form=status_form,
        note_form=note_form
    )

@admin_bp.route('/export-csv')
@admin_required
def export_csv():
    """Export filtered or all complaints to a CSV file for demonstration records."""
    search_keyword = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = Complaint.query
    if search_keyword:
        query = query.filter(
            (Complaint.reference_number.ilike(f'%{search_keyword}%')) |
            (Complaint.title.ilike(f'%{search_keyword}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'Reference Number',
        'Title',
        'Category',
        'Status',
        'Complainant Name',
        'Complainant Email',
        'Incident Date',
        'Incident Location',
        'Submission Date',
        'Last Updated Date'
    ])

    for c in complaints:
        writer.writerow([
            c.reference_number,
            c.title,
            c.category,
            c.status,
            c.complainant.full_name,
            c.complainant.email,
            c.incident_date.strftime('%Y-%m-%d') if c.incident_date else '',
            c.incident_location,
            c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            c.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=crimeconnect_complaints_export.csv'}
    )

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """JSON API providing categorized and status distribution data for Chart.js."""
    category_data = {cat: Complaint.query.filter_by(category=cat).count() for cat in Complaint.CATEGORIES}
    status_data = {stat: Complaint.query.filter_by(status=stat).count() for stat in Complaint.STATUSES}

    return jsonify({
        'categories': category_data,
        'statuses': status_data
    })
