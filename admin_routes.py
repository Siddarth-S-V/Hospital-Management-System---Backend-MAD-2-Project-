from flask import Blueprint, request, jsonify, session
from models import db, User, Appointment
from utils import login_required, role_required
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/create_user', methods=['POST'])
@role_required('admin')
def create_user():
    """Create doctor or patient"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate role
        if data['role'] not in ['doctor', 'patient']:
            return jsonify({'error': 'Role must be doctor or patient'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            role=data['role'],
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Clear doctors cache if creating a doctor
        if data['role'] == 'doctor':
            from utils import redis_client
            redis_client.delete('doctors_list')

        return jsonify({
            'message': f'{data["role"].title()} created successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@admin_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """Update user profile"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prevent admin from updating other admins
        if user.role == 'admin' and user.id != session['user_id']:
            return jsonify({'error': 'Cannot update other admin accounts'}), 403

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

        # Clear doctors cache if updating a doctor
        if user.role == 'doctor':
            from utils import redis_client
            redis_client.delete('doctors_list')

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500

@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """Delete user (doctor or patient)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prevent admin from deleting other admins or themselves
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin accounts'}), 403

        # Check for active appointments
        active_appointments = Appointment.query.filter(
            or_(Appointment.doctor_id == user_id, Appointment.patient_id == user_id),
            Appointment.status == 'booked'
        ).count()

        if active_appointments > 0:
            return jsonify({'error': 'Cannot delete user with active appointments'}), 400

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Clear doctors cache if deleting a doctor
        if user.role == 'doctor':
            from utils import redis_client
            redis_client.delete('doctors_list')

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

@admin_bp.route('/search', methods=['GET'])
@role_required('admin')
def search_users():
    """Search users by name or email"""
    try:
        query = request.args.get('q', '').strip()
        role = request.args.get('role', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Build query
        users_query = User.query.filter(User.role != 'admin')  # Exclude admins

        if role and role in ['doctor', 'patient']:
            users_query = users_query.filter_by(role=role)

        if query:
            users_query = users_query.filter(
                or_(
                    User.name.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            )

        # Paginate results
        users_pagination = users_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'users': [user.to_dict() for user in users_pagination.items],
            'total': users_pagination.total,
            'pages': users_pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@admin_bp.route('/appointments', methods=['GET'])
@role_required('admin')
def view_appointments():
    """View all appointments"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', '')

        # Build query
        appointments_query = Appointment.query

        if status and status in ['booked', 'completed', 'cancelled']:
            appointments_query = appointments_query.filter_by(status=status)

        # Order by date and time
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
        return jsonify({'error': f'Failed to get appointments: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'total_doctors': User.query.filter_by(role='doctor').count(),
            'total_patients': User.query.filter_by(role='patient').count(),
            'total_appointments': Appointment.query.count(),
            'booked_appointments': Appointment.query.filter_by(status='booked').count(),
            'completed_appointments': Appointment.query.filter_by(status='completed').count(),
            'cancelled_appointments': Appointment.query.filter_by(status='cancelled').count()
        }

        return jsonify({'stats': stats}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500
