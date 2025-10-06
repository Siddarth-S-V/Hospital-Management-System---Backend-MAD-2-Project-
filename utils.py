from functools import wraps
from flask import session, jsonify, current_app
from flask_mail import Message
import csv
import os
from datetime import datetime
import redis

# Redis client
redis_client = redis.Redis.from_url('redis://localhost:6379/0', decode_responses=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            if session.get('role') != required_role:
                return jsonify({'error': f'{required_role} access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_email(subject, recipients, html_body, text_body=None):
    """Send email using Flask-Mail"""
    try:
        from app import mail
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def generate_csv_export(user_id, appointments_data):
    """Generate CSV file for appointment history"""
    try:
        filename = f"appointments_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Ensure exports directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Time', 'Doctor', 'Status', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for appointment in appointments_data:
                writer.writerow({
                    'Date': appointment.get('date', ''),
                    'Time': appointment.get('time', ''),
                    'Doctor': appointment.get('doctor_name', ''),
                    'Status': appointment.get('status', ''),
                    'Notes': appointment.get('notes', '')
                })

        return filename
    except Exception as e:
        current_app.logger.error(f"Failed to generate CSV: {str(e)}")
        return None

def cache_doctors_list():
    """Cache doctors list in Redis"""
    try:
        from models import User
        doctors = User.query.filter_by(role='doctor').all()
        doctors_data = [doctor.to_dict() for doctor in doctors]

        # Cache for 1 hour
        redis_client.setex('doctors_list', 3600, str(doctors_data))
        return doctors_data
    except Exception as e:
        current_app.logger.error(f"Failed to cache doctors list: {str(e)}")
        return []

def get_cached_doctors_list():
    """Get doctors list from Redis cache"""
    try:
        cached_data = redis_client.get('doctors_list')
        if cached_data:
            return eval(cached_data)  # In production, use json.loads instead
        else:
            return cache_doctors_list()
    except Exception as e:
        current_app.logger.error(f"Failed to get cached doctors list: {str(e)}")
        return cache_doctors_list()

def cache_doctor_availability(doctor_id):
    """Cache doctor availability in Redis"""
    try:
        from models import Availability
        availability = Availability.query.filter_by(doctor_id=doctor_id).all()
        availability_data = [avail.to_dict() for avail in availability]

        # Cache for 6 hours
        redis_client.setex(f'doctor_availability_{doctor_id}', 21600, str(availability_data))
        return availability_data
    except Exception as e:
        current_app.logger.error(f"Failed to cache doctor availability: {str(e)}")
        return []

def get_cached_doctor_availability(doctor_id):
    """Get doctor availability from Redis cache"""
    try:
        cached_data = redis_client.get(f'doctor_availability_{doctor_id}')
        if cached_data:
            return eval(cached_data)  # In production, use json.loads instead
        else:
            return cache_doctor_availability(doctor_id)
    except Exception as e:
        current_app.logger.error(f"Failed to get cached doctor availability: {str(e)}")
        return cache_doctor_availability(doctor_id)

def is_double_booking(doctor_id, date, time, appointment_id=None):
    """Check if appointment time conflicts with existing bookings"""
    try:
        from models import Appointment
        query = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=date,
            time=time,
            status='booked'
        )

        # Exclude current appointment if updating
        if appointment_id:
            query = query.filter(Appointment.id != appointment_id)

        existing_appointment = query.first()
        return existing_appointment is not None
    except Exception as e:
        current_app.logger.error(f"Failed to check double booking: {str(e)}")
        return True  # Err on the side of caution
