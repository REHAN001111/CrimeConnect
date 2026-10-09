from flask import Blueprint, render_template
from models import Complaint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Public home page with platform statistics, hero, and educational guidance."""
    # Fictional aggregated counter for visual demonstration
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter_by(status=Complaint.STATUS_RESOLVED).count()
    under_review = Complaint.query.filter_by(status=Complaint.STATUS_UNDER_REVIEW).count()
    
    return render_template(
        'index.html',
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        under_review=under_review
    )

@main_bp.route('/about')
def about():
    """Academic project overview, architectural design, and objectives."""
    return render_template('about.html')

@main_bp.route('/faq')
def faq():
    """Frequently asked questions for complainants and administrators."""
    return render_template('faq.html')
