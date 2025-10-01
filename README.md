Hospital Management System - Backend (MAD-2 Project)
A comprehensive Hospital Management System built with Flask, Vue.js, SQLite, Redis, and Celery.

🏥 Project Overview
This is a full-stack Hospital Management System that allows Admins, Doctors, and Patients to interact with the system based on their roles. The system includes appointment scheduling, patient management, doctor management, and automated background jobs.

🛠️ Technology Stack
Backend (Flask)
Flask: Web framework for API development

SQLAlchemy: ORM for database operations

SQLite: Database for storing all application data

Redis: Message broker for Celery

Celery: Background task processing

Frontend (Vue.js)
Vue.js 3: Progressive JavaScript framework

Bootstrap: CSS framework for styling

Axios: HTTP client for API requests

📋 Features
👨‍💼 Admin Features
Dashboard with statistics (doctors, patients, appointments)

Doctor management (Add, Edit, Delete)

Patient management (View, Edit, Delete)

View all appointments with filtering

Search functionality for doctors and patients

👩‍⚕️ Doctor Features
Personal dashboard with today's appointments

View upcoming appointments for the week

Mark appointments as completed/cancelled

Add diagnosis and treatment notes

Manage availability (7-day schedule)

View patient medical history

🏥 Patient Features
Registration and login

Browse departments and specializations

Search and book appointments with doctors

View appointment history and treatment details

Cancel/reschedule appointments

Export treatment history as CSV

🔄 Background Jobs (Celery)
Daily Appointment Reminders: Automated reminders sent every morning

Monthly Doctor Reports: Activity reports generated on 1st of each month

CSV Export: Async patient treatment history export

🚀 Quick Start
Prerequisites
Python 3.8+

Redis server

Node.js (for frontend)

Installation
Clone the repository

bash
git clone <repository-url>
cd hospital-management-system
Backend Setup

bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations
Start Redis (using Docker)

bash
docker-compose up -d redis
Initialize Database

bash
python app.py
# Database tables will be created automatically
Start Flask Application

bash
python app.py
# Server will start at http://localhost:5000
Start Celery Worker (in a separate terminal)

bash
python run_celery.py worker
Start Celery Beat Scheduler (in another terminal)

bash
python run_celery.py beat
Frontend Setup
Navigate to frontend directory

bash
cd frontend
Install dependencies

bash
npm install
Start development server

bash
npm run serve
# Frontend will start at http://localhost:8080
📊 Database Schema
Core Tables
users: Authentication data for all user types

departments: Hospital departments/specializations

doctors: Doctor profiles and information

patients: Patient profiles and medical history

appointments: Appointment scheduling and status

treatments: Medical records and prescriptions

doctor_availability: Doctor scheduling for 7 days

🔌 API Endpoints
Authentication
POST /api/auth/login - User login

POST /api/auth/register - Patient registration

POST /api/auth/logout - User logout

Admin Routes
GET /api/admin/dashboard - Admin dashboard data

GET /api/admin/doctors - List all doctors

POST /api/admin/doctors - Create new doctor

PUT /api/admin/doctors/<id> - Update doctor

DELETE /api/admin/doctors/<id> - Delete doctor

Doctor Routes
GET /api/doctor/dashboard - Doctor dashboard

POST /api/doctor/appointments/<id>/complete - Mark appointment complete

GET /api/doctor/patients/<id>/history - Patient medical history

Patient Routes
GET /api/patient/dashboard - Patient dashboard

GET /api/patient/doctors - Search doctors

POST /api/patient/export-treatments - Export treatment CSV

Appointment Routes
POST /api/appointments - Book appointment

PUT /api/appointments/<id> - Reschedule appointment

POST /api/appointments/<id>/cancel - Cancel appointment

⚙️ Background Jobs
Scheduled Jobs
Daily Reminders (8:00 AM daily)

Sends appointment reminders to patients

Uses email/SMS/Google Chat webhooks

Monthly Reports (1st of each month)

Generates HTML activity reports for doctors

Includes appointment statistics and treatment summaries

User-Triggered Jobs
CSV Export (On-demand)

Exports patient treatment history

Provides downloadable CSV file

🎨 UI/UX Features
Responsive Design: Works on desktop and mobile

Role-based Navigation: Different interfaces for each user type

Real-time Updates: Dynamic status changes

Professional Medical Theme: Clean, hospital-appropriate design

Form Validation: Client and server-side validation

Search & Filter: Advanced search capabilities

🔒 Security Features
Password Hashing: Secure password storage with Werkzeug

Session Management: Flask session-based authentication

Role-based Access Control: Different permissions for each role

Input Validation: Prevents SQL injection and XSS

CORS Support: Secure cross-origin requests

📈 Performance Optimizations
Database Indexing: Optimized queries with proper indexes

Caching: Redis caching for frequently accessed data

Pagination: Large datasets split into pages

Async Processing: Background jobs don't block user requests

🧪 Testing
bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
📦 Deployment
Production Setup
Set environment variables for production

Use PostgreSQL instead of SQLite

Configure proper email service (SendGrid, AWS SES)

Set up Redis cluster for high availability

Use Gunicorn as WSGI server

Configure Nginx as reverse proxy

👥 Default Users
The system creates a default admin user:

Username: admin

Password: admin123

Role: Admin

📝 Project Requirements Compliance
✅ Mandatory Frameworks

Flask for API

Vue.js for UI

SQLite for database

Redis for caching

Celery for background jobs

✅ Core Features

Role-based authentication

CRUD operations for all entities

Appointment management

Background job processing

Search and filter capabilities

✅ Database Design

Programmatically created tables

Proper relationships and constraints

Normalized schema design

🤝 Contributing
Fork the repository

Create a feature branch

Make your changes

Add tests for new functionality

Submit a pull request

📄 License
This project is created for educational purposes as part of MAD-2 coursework.

📞 Support
For issues and questions, please create an issue in the GitHub repository.
