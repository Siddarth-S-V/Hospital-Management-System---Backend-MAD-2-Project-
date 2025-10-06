from flask import Flask, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from config import Config
import os

# Initialize extensions
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    from models import db
    db.init_app(app)
    mail.init_app(app)

    # Enable CORS for frontend
    CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

    # Register blueprints
    from auth import auth_bp
    from admin_routes import admin_bp
    from doctor_routes import doctor_bp
    from patient_routes import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        create_default_admin()

        # Create exports directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Medical Appointment System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/*',
                'admin': '/api/admin/*',
                'doctor': '/api/doctor/*',
                'patient': '/api/patient/*'
            }
        })

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': str(datetime.utcnow())}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app

def create_default_admin():
    """Create default admin account if it doesn't exist"""
    from models import db, User

    admin = User.query.filter_by(email='admin@medical.com').first()
    if not admin:
        admin = User(
            name='System Administrator',
            email='admin@medical.com',
            role='admin',
            phone='1234567890'
        )
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()

        print("✅ Default admin created:")
        print("   Email: admin@medical.com")
        print("   Password: admin123")
        print("   ⚠️  Please change password after first login!")

if __name__ == '__main__':
    from datetime import datetime

    app = create_app()

    print("🏥 Medical Appointment System API")
    print("=" * 40)
    print("🚀 Starting Flask development server...")
    print("📱 Frontend: http://localhost:5173")
    print("🔗 API: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5000)
