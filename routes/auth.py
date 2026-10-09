from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from extensions import db
from models import User, Complaint
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

def is_safe_url(target):
    """Ensure redirect URL is strictly internal to prevent open redirect vulnerabilities."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc or not test_url.netloc

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new citizen user account. Admin accounts can only be created via CLI."""
    if current_user.is_authenticated:
        return redirect(url_for('complaints.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip() if form.phone.data else None,
            role='user'  # Hardcoded role: security rule prevents self-privilege elevation
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in to submit and track complaints.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate registered users or administrators."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('complaints.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email_clean = form.email.data.strip().lower()
        user = User.query.filter_by(email=email_clean).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Safe next redirection
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('complaints.dashboard'))
        else:
            flash('Invalid email or password. Please verify your credentials.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Terminate the current user session."""
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User account profile and activity overview."""
    total_submitted = Complaint.query.filter_by(user_id=current_user.id).count()
    resolved = Complaint.query.filter_by(
        user_id=current_user.id,
        status=Complaint.STATUS_RESOLVED
    ).count()
    under_review = Complaint.query.filter_by(
        user_id=current_user.id,
        status=Complaint.STATUS_UNDER_REVIEW
    ).count()

    return render_template(
        'profile.html',
        total_submitted=total_submitted,
        resolved=resolved,
        under_review=under_review
    )
