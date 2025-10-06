from flask import Blueprint, request, jsonify, session
from models import db, User, Appointment, TreatmentHistory, Specialization
from utils import login_required, role_required, get_cached_doctors_list, is_double_booking
from datetime import datetime, date, time, timedelta
from tasks import export_patient_history

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/update_profile', methods=['PUT'])
@role_required('patient')
def update_profile():
    """Update patient profile"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data and data['email'] != user.email:
            # Check if new email is already taken
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 400
            user.email = data['email']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@patient_bp.route('/specializations', methods=['GET'])
@role_required('patient')
def get_specializations():
    """Get all available specializations/departments"""
    try:
        # Get specializations from database
        specializations = Specialization.query.all()
        spec_list = [spec.to_dict() for spec in specializations]

        # If no specializations in DB, get from doctors
        if not spec_list:
            doctors = User.query.filter_by(role='doctor').filter(User.specialization.isnot(None)).all()
            unique_specs = list(set([doc.specialization for doc in doctors if doc.specialization]))
            spec_list = [{'name': spec, 'description': ''} for spec in unique_specs]

        return jsonify({'specializations': spec_list}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get specializations: {str(e)}'}), 500

@patient_bp.route('/doctors', methods=['GET'])
@role_required('patient')
def get_doctors():
    """Get list of available doctors with enhanced filtering"""
    try:
        search_query = request.args.get('search', '').strip()
        specialization = request.args.get('specialization', '').strip()

        # Get cached doctors list
        doctors = get_cached_doctors_list()

        # Filter by search query if provided
        if search_query:
            doctors = [
                doctor for doctor in doctors 
                if search_query.lower() in doctor['name'].lower() or 
                   search_query.lower() in doctor['email'].lower() or
                   (doctor.get('specialization') and search_query.lower() in doctor['specialization'].lower())
            ]

        # Filter by specialization
        if specialization:
            doctors = [
                doctor for doctor in doctors 
                if doctor.get('specialization') and specialization.lower() in doctor['specialization'].lower()
            ]

        return jsonify({'doctors': doctors}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get doctors: {str(e)}'}), 500

@patient_bp.route('/doctor/<int:doctor_id>/profile', methods=['GET'])
@role_required('patient')
def get_doctor_profile(doctor_id):
    """Get detailed doctor profile"""
    try:
        doctor = User.query.filter_by(id=doctor_id, role='doctor').first()
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Get doctor's availability
        from utils import get_cached_doctor_availability
        availability = get_cached_doctor_availability(doctor_id)

        # Get total appointments and completed appointments
        total_appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
        completed_appointments = Appointment.query.filter_by(doctor_id=doctor_id, status='completed').count()

        # Get recent reviews/ratings if any
        recent_treatments = TreatmentHistory.query.filter_by(doctor_id=doctor_id).order_by(
            TreatmentHistory.created_at.desc()
        ).limit(5).all()

        profile_data = doctor.to_dict()
        profile_data.update({
            'availability': availability,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'recent_treatments': [treatment.to_dict() for treatment in recent_treatments]
        })

        return jsonify({'doctor_profile': profile_data}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get doctor profile: {str(e)}'}), 500

@patient_bp.route('/doctor/<int:doctor_id>/availability', methods=['GET'])
@role_required('patient')
def get_doctor_availability(doctor_id):
    """Get specific doctor's availability for next 7 days"""
    try:
        from utils import get_cached_doctor_availability

        availability = get_cached_doctor_availability(doctor_id)

        # Generate next 7 days availability
        next_7_days = []
        today = date.today()

        for i in range(7):
            check_date = today + timedelta(days=i)
            day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday

            # Find availability for this day
            day_availability = [avail for avail in availability if avail['day_of_week'] == day_of_week]

            # Get existing appointments for this day
            existing_appointments = Appointment.query.filter_by(
                doctor_id=doctor_id,
                date=check_date,
                status='booked'
            ).all()

            booked_times = [app.time.strftime('%H:%M') for app in existing_appointments]

            day_data = {
                'date': check_date.isoformat(),
                'day_name': check_date.strftime('%A'),
                'availability': day_availability,
                'booked_times': booked_times,
                'is_available': len(day_availability) > 0
            }

            next_7_days.append(day_data)

        return jsonify({
            'doctor_id': doctor_id,
            'next_7_days': next_7_days
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get doctor availability: {str(e)}'}), 500

@patient_bp.route('/book', methods=['POST'])
@role_required('patient')
def book_appointment():
    """Book new appointment"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['doctor_id', 'date', 'time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate doctor exists
        doctor = User.query.filter_by(id=data['doctor_id'], role='doctor').first()
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Parse and validate date/time
        try:
            appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400

        # Check if date is in the future
        if appointment_date <= date.today():
            return jsonify({'error': 'Appointment date must be in the future'}), 400

        # Check for double booking
        if is_double_booking(data['doctor_id'], appointment_date, appointment_time):
            return jsonify({'error': 'Time slot already booked. Please choose another time.'}), 400

        # Create appointment
        appointment = Appointment(
            patient_id=session['user_id'],
            doctor_id=data['doctor_id'],
            date=appointment_date,
            time=appointment_time,
            notes=data.get('notes', ''),
            status='booked'
        )

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to book appointment: {str(e)}'}), 500

@patient_bp.route('/reschedule/<int:appointment_id>', methods=['PUT'])
@role_required('patient')
def reschedule_appointment(appointment_id):
    """Reschedule existing appointment"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Check if appointment belongs to this patient
        if appointment.patient_id != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403

        # Check if appointment can be rescheduled
        if appointment.status != 'booked':
            return jsonify({'error': 'Only booked appointments can be rescheduled'}), 400

        data = request.get_json()

        # Validate required fields
        if not data.get('date') or not data.get('time'):
            return jsonify({'error': 'Date and time are required'}), 400

        # Parse and validate new date/time
        try:
            new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            new_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400

        # Check if new date is in the future
        if new_date <= date.today():
            return jsonify({'error': 'Appointment date must be in the future'}), 400

        # Check for double booking (excluding current appointment)
        if is_double_booking(appointment.doctor_id, new_date, new_time, appointment_id):
            return jsonify({'error': 'Time slot already booked. Please choose another time.'}), 400

        # Update appointment
        appointment.date = new_date
        appointment.time = new_time
        appointment.updated_at = datetime.utcnow()

        if 'notes' in data:
            appointment.notes = data['notes']

        db.session.commit()

        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reschedule appointment: {str(e)}'}), 500

@patient_bp.route('/cancel/<int:appointment_id>', methods=['DELETE'])
@role_required('patient')
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Check if appointment belongs to this patient
        if appointment.patient_id != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403

        # Check if appointment can be cancelled
        if appointment.status == 'cancelled':
            return jsonify({'error': 'Appointment already cancelled'}), 400

        # Cancel appointment
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel appointment: {str(e)}'}), 500

@patient_bp.route('/history', methods=['GET'])
@role_required('patient')
def get_history():
    """Get patient's appointment history with diagnosis and prescriptions"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', '')

        # Build query for patient's appointments
        appointments_query = Appointment.query.filter_by(patient_id=session['user_id'])

        if status and status in ['booked', 'completed', 'cancelled']:
            appointments_query = appointments_query.filter_by(status=status)

        # Order by date and time (most recent first)
        appointments_query = appointments_query.order_by(
            Appointment.date.desc(),
            Appointment.time.desc()
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
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

@patient_bp.route('/treatment_history', methods=['GET'])
@role_required('patient')
def get_treatment_history():
    """Get patient's detailed treatment history with diagnosis and prescriptions"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Get treatment history for this patient
        treatments_query = TreatmentHistory.query.filter_by(patient_id=session['user_id'])
        treatments_query = treatments_query.order_by(TreatmentHistory.created_at.desc())

        # Paginate results
        treatments_pagination = treatments_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'treatments': [treatment.to_dict() for treatment in treatments_pagination.items],
            'total': treatments_pagination.total,
            'pages': treatments_pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get treatment history: {str(e)}'}), 500

@patient_bp.route('/export_history', methods=['POST'])
@role_required('patient')
def export_history():
    """Trigger async CSV export of appointment history"""
    try:
        # Trigger Celery task
        task = export_patient_history.delay(session['user_id'])

        return jsonify({
            'message': 'Export started. You will receive an email when ready.',
            'task_id': task.id
        }), 202

    except Exception as e:
        return jsonify({'error': f'Failed to start export: {str(e)}'}), 500

@patient_bp.route('/upcoming_appointments', methods=['GET'])
@role_required('patient')
def get_upcoming_appointments():
    """Get patient's upcoming appointments with status"""
    try:
        today = date.today()

        appointments = Appointment.query.filter(
            Appointment.patient_id == session['user_id'],
            Appointment.status == 'booked',
            Appointment.date >= today
        ).order_by(
            Appointment.date.asc(),
            Appointment.time.asc()
        ).limit(5).all()

        return jsonify({
            'appointments': [appointment.to_dict() for appointment in appointments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get upcoming appointments: {str(e)}'}), 500

@patient_bp.route('/dashboard_data', methods=['GET'])
@role_required('patient')
def get_dashboard_data():
    """Get all dashboard data in one call"""
    try:
        today = date.today()

        # Upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == session['user_id'],
            Appointment.status == 'booked',
            Appointment.date >= today
        ).order_by(
            Appointment.date.asc(),
            Appointment.time.asc()
        ).limit(5).all()

        # Past appointments with diagnosis
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == session['user_id'],
            Appointment.status == 'completed',
            Appointment.date < today
        ).order_by(
            Appointment.date.desc()
        ).limit(5).all()

        # Available specializations
        specializations = Specialization.query.all()
        if not specializations:
            # Get from doctors if no specializations in DB
            doctors = User.query.filter_by(role='doctor').filter(User.specialization.isnot(None)).all()
            unique_specs = list(set([doc.specialization for doc in doctors if doc.specialization]))
            specializations = [{'name': spec, 'description': ''} for spec in unique_specs]
        else:
            specializations = [spec.to_dict() for spec in specializations]

        return jsonify({
            'upcoming_appointments': [app.to_dict() for app in upcoming_appointments],
            'past_appointments': [app.to_dict() for app in past_appointments],
            'specializations': specializations
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard data: {str(e)}'}), 500
