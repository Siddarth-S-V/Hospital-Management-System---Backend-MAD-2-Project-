from flask import Blueprint, request, jsonify, session
from models import db, User, Appointment, Availability, TreatmentHistory
from utils import login_required, role_required, cache_doctor_availability
from datetime import datetime, date, time
from sqlalchemy import and_

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/appointments', methods=['GET'])
@role_required('doctor')
def get_appointments():
    """View doctor's appointments"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', '')
        date_filter = request.args.get('date', '')

        # Build query for doctor's appointments
        appointments_query = Appointment.query.filter_by(doctor_id=session['user_id'])

        if status and status in ['booked', 'completed', 'cancelled']:
            appointments_query = appointments_query.filter_by(status=status)

        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                appointments_query = appointments_query.filter_by(date=filter_date)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Order by date and time
        appointments_query = appointments_query.order_by(
            Appointment.date.asc(),
            Appointment.time.asc()
        )

        # Paginate results
        appointments_pagination = appointments_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'appointments': [appointment.to_dict() for appointment in appointments_pagination.items],
            'total': appointments_pagination.total,
            'pages': appointments_pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get appointments: {str(e)}'}), 500

@doctor_bp.route('/appointment/<int:appointment_id>/status', methods=['PUT'])
@role_required('doctor')
def update_appointment_status(appointment_id):
    """Mark appointment as completed or cancelled"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Check if appointment belongs to this doctor
        if appointment.doctor_id != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['completed', 'cancelled']:
            return jsonify({'error': 'Status must be completed or cancelled'}), 400

        appointment.status = new_status
        appointment.notes = data.get('notes', appointment.notes)
        appointment.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': f'Appointment marked as {new_status}',
            'appointment': appointment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update appointment: {str(e)}'}), 500

@doctor_bp.route('/history/update', methods=['POST'])
@role_required('doctor')
def update_treatment_history():
    """Add treatment history"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['appointment_id', 'summary']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if appointment exists and belongs to this doctor
        appointment = Appointment.query.get(data['appointment_id'])
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment.doctor_id != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403

        # Create treatment history
        treatment = TreatmentHistory(
            doctor_id=session['user_id'],
            patient_id=appointment.patient_id,
            appointment_id=data['appointment_id'],
            summary=data['summary']
        )

        db.session.add(treatment)

        # Mark appointment as completed if not already
        if appointment.status == 'booked':
            appointment.status = 'completed'
            appointment.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Treatment history added successfully',
            'treatment': treatment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add treatment history: {str(e)}'}), 500

@doctor_bp.route('/availability', methods=['POST'])
@role_required('doctor')
def set_availability():
    """Set doctor's weekly availability"""
    try:
        data = request.get_json()

        if not isinstance(data.get('availability'), list):
            return jsonify({'error': 'Availability must be a list of 7 days'}), 400

        # Clear existing availability
        Availability.query.filter_by(doctor_id=session['user_id']).delete()

        # Add new availability
        for day_data in data['availability']:
            if not isinstance(day_data, dict):
                continue

            day_of_week = day_data.get('day_of_week')
            start_time_str = day_data.get('start_time')
            end_time_str = day_data.get('end_time')

            # Validate day of week
            if day_of_week is None or day_of_week < 0 or day_of_week > 6:
                continue

            # Skip if no time provided (day off)
            if not start_time_str or not end_time_str:
                continue

            try:
                # Parse time strings
                start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()

                # Validate time range
                if start_time_obj >= end_time_obj:
                    return jsonify({'error': f'Invalid time range for day {day_of_week}'}), 400

                availability = Availability(
                    doctor_id=session['user_id'],
                    day_of_week=day_of_week,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )

                db.session.add(availability)

            except ValueError:
                return jsonify({'error': f'Invalid time format for day {day_of_week}. Use HH:MM'}), 400

        db.session.commit()

        # Update cache
        cache_doctor_availability(session['user_id'])

        return jsonify({'message': 'Availability updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to set availability: {str(e)}'}), 500

@doctor_bp.route('/availability', methods=['GET'])
@role_required('doctor')
def get_availability():
    """Get doctor's current availability"""
    try:
        availability = Availability.query.filter_by(doctor_id=session['user_id']).all()

        return jsonify({
            'availability': [avail.to_dict() for avail in availability]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get availability: {str(e)}'}), 500

@doctor_bp.route('/patients', methods=['GET'])
@role_required('doctor')
def get_patients():
    """Get list of patients who have appointments with this doctor"""
    try:
        # Get unique patients from appointments
        patients_query = db.session.query(User).join(
            Appointment, User.id == Appointment.patient_id
        ).filter(
            Appointment.doctor_id == session['user_id']
        ).distinct()

        patients = patients_query.all()

        return jsonify({
            'patients': [patient.to_dict() for patient in patients]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get patients: {str(e)}'}), 500

@doctor_bp.route('/stats', methods=['GET'])
@role_required('doctor')
def get_doctor_stats():
    """Get doctor's statistics"""
    try:
        doctor_id = session['user_id']

        stats = {
            'total_appointments': Appointment.query.filter_by(doctor_id=doctor_id).count(),
            'completed_appointments': Appointment.query.filter_by(doctor_id=doctor_id, status='completed').count(),
            'booked_appointments': Appointment.query.filter_by(doctor_id=doctor_id, status='booked').count(),
            'cancelled_appointments': Appointment.query.filter_by(doctor_id=doctor_id, status='cancelled').count(),
            'total_patients': db.session.query(User).join(
                Appointment, User.id == Appointment.patient_id
            ).filter(Appointment.doctor_id == doctor_id).distinct().count()
        }

        return jsonify({'stats': stats}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500
