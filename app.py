import os
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, csrf
from routes.main import main_bp
from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    """Application factory for CrimeConnect."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload directories exist
    os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(admin_bp)

    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html', error=error), 400

    # Global context processor
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'CrimeConnect',
            'current_year': 2026,
            'disclaimer_notice': (
                'ACADEMIC DEMONSTRATION PROTOTYPE: CrimeConnect is an educational ITL project. '
                'It is NOT connected to any official law enforcement or emergency services agency. '
                'In real emergencies, call 911 / 112 / 100.'
            )
        }

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    print("==================================================")
    print(" CrimeConnect - Online Crime Reporting System     ")
    print(" Running at http://127.0.0.1:5000/                ")
    print(" Disclaimer: Educational demonstration only.      ")
    print("==================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
