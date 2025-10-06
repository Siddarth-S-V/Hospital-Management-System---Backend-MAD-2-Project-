from celery import Celery
from celery.schedules import crontab
from datetime import datetime, date
import os

# Initialize Celery
celery = Celery('medical_appointment_tasks')
celery.config_from_object('config.Config')

# Configure beat schedule
celery.conf.beat_schedule = {
    'daily-reminder': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
    'monthly-report': {
        'task': 'tasks.send_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9:00 AM
    },
}

@celery.task(bind=True)
def send_daily_reminders(self):
    """Send daily appointment reminders to patients"""
    try:
        from app import create_app
        from models import db, User, Appointment
        from utils import send_email

        app = create_app()

        with app.app_context():
            today = date.today()

            # Get all appointments for today
            appointments = Appointment.query.filter(
                Appointment.date == today,
                Appointment.status == 'booked'
            ).all()

            sent_count = 0

            for appointment in appointments:
                patient = appointment.patient
                doctor = appointment.doctor

                if patient and patient.email:
                    # Prepare email content
                    subject = f"Appointment Reminder - {appointment.date}"

                    html_body = f"""
                    <html>
                    <body>
                        <h2>Appointment Reminder</h2>
                        <p>Dear {patient.name},</p>
                        <p>This is a reminder that you have an appointment scheduled for today:</p>
                        <ul>
                            <li><strong>Date:</strong> {appointment.date}</li>
                            <li><strong>Time:</strong> {appointment.time.strftime('%H:%M')}</li>
                            <li><strong>Doctor:</strong> {doctor.name}</li>
                        </ul>
                        <p>Please arrive 15 minutes early for your appointment.</p>
                        <p>Best regards,<br>Medical Appointment System</p>
                    </body>
                    </html>
                    """

                    text_body = f"""
                    Appointment Reminder

                    Dear {patient.name},

                    This is a reminder that you have an appointment scheduled for today:
                    - Date: {appointment.date}
                    - Time: {appointment.time.strftime('%H:%M')}
                    - Doctor: {doctor.name}

                    Please arrive 15 minutes early for your appointment.

                    Best regards,
                    Medical Appointment System
                    """

                    # Send email
                    if send_email(subject, patient.email, html_body, text_body):
                        sent_count += 1

            return f"Daily reminders sent: {sent_count} emails"

    except Exception as e:
        self.retry(countdown=300, max_retries=3)  # Retry after 5 minutes, max 3 times
        return f"Failed to send daily reminders: {str(e)}"

@celery.task(bind=True)
def send_monthly_reports(self):
    """Send monthly activity reports to doctors"""
    try:
        from app import create_app
        from models import db, User, Appointment, TreatmentHistory
        from utils import send_email
        from sqlalchemy import func, extract

        app = create_app()

        with app.app_context():
            # Get previous month data
            now = datetime.now()
            if now.month == 1:
                prev_month = 12
                prev_year = now.year - 1
            else:
                prev_month = now.month - 1
                prev_year = now.year

            # Get all doctors
            doctors = User.query.filter_by(role='doctor').all()
            sent_count = 0

            for doctor in doctors:
                # Get doctor's monthly statistics
                appointments_count = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    extract('month', Appointment.date) == prev_month,
                    extract('year', Appointment.date) == prev_year
                ).count()

                completed_count = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.status == 'completed',
                    extract('month', Appointment.date) == prev_month,
                    extract('year', Appointment.date) == prev_year
                ).count()

                cancelled_count = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.status == 'cancelled',
                    extract('month', Appointment.date) == prev_month,
                    extract('year', Appointment.date) == prev_year
                ).count()

                treatments_count = TreatmentHistory.query.filter(
                    TreatmentHistory.doctor_id == doctor.id,
                    extract('month', TreatmentHistory.created_at) == prev_month,
                    extract('year', TreatmentHistory.created_at) == prev_year
                ).count()

                # Prepare email content
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                month_name = month_names[prev_month - 1]

                subject = f"Monthly Activity Report - {month_name} {prev_year}"

                html_body = f"""
                <html>
                <body>
                    <h2>Monthly Activity Report</h2>
                    <p>Dear Dr. {doctor.name},</p>
                    <p>Here's your activity summary for {month_name} {prev_year}:</p>

                    <table border="1" style="border-collapse: collapse; width: 100%;">
                        <tr>
                            <th style="padding: 10px; background-color: #f2f2f2;">Metric</th>
                            <th style="padding: 10px; background-color: #f2f2f2;">Count</th>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Total Appointments</td>
                            <td style="padding: 10px;">{appointments_count}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Completed Appointments</td>
                            <td style="padding: 10px;">{completed_count}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Cancelled Appointments</td>
                            <td style="padding: 10px;">{cancelled_count}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Treatment Records Added</td>
                            <td style="padding: 10px;">{treatments_count}</td>
                        </tr>
                    </table>

                    <p>Thank you for your continued service!</p>
                    <p>Best regards,<br>Medical Appointment System</p>
                </body>
                </html>
                """

                # Send email if doctor has an email
                if doctor.email:
                    if send_email(subject, doctor.email, html_body):
                        sent_count += 1

            return f"Monthly reports sent: {sent_count} emails"

    except Exception as e:
        self.retry(countdown=300, max_retries=3)
        return f"Failed to send monthly reports: {str(e)}"

@celery.task(bind=True)
def export_patient_history(self, patient_id):
    """Generate and email CSV export of patient history"""
    try:
        from app import create_app
        from models import db, User, Appointment
        from utils import generate_csv_export, send_email

        app = create_app()

        with app.app_context():
            # Get patient
            patient = User.query.get(patient_id)
            if not patient:
                return "Patient not found"

            # Get patient's appointments
            appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
                Appointment.date.desc(),
                Appointment.time.desc()
            ).all()

            appointments_data = [appointment.to_dict() for appointment in appointments]

            # Generate CSV file
            filename = generate_csv_export(patient_id, appointments_data)

            if filename:
                # Send email with CSV attachment info
                subject = "Your Appointment History Export is Ready"

                html_body = f"""
                <html>
                <body>
                    <h2>Appointment History Export</h2>
                    <p>Dear {patient.name},</p>
                    <p>Your appointment history export has been generated successfully.</p>
                    <p>The CSV file contains {len(appointments_data)} appointment records.</p>
                    <p>File: {filename}</p>
                    <p>You can download it from your patient dashboard.</p>
                    <p>Best regards,<br>Medical Appointment System</p>
                </body>
                </html>
                """

                text_body = f"""
                Appointment History Export

                Dear {patient.name},

                Your appointment history export has been generated successfully.
                The CSV file contains {len(appointments_data)} appointment records.
                File: {filename}

                You can download it from your patient dashboard.

                Best regards,
                Medical Appointment System
                """

                send_email(subject, patient.email, html_body, text_body)

                return f"CSV export completed for patient {patient_id}: {filename}"
            else:
                return "Failed to generate CSV export"

    except Exception as e:
        self.retry(countdown=60, max_retries=3)
        return f"Failed to export patient history: {str(e)}"

if __name__ == '__main__':
    celery.start()
