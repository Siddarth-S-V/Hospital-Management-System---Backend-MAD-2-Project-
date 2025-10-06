<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-user"></i> Patient Dashboard
        </h1>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center h-100">
          <div class="card-body">
            <i class="fas fa-calendar-plus fa-2x text-primary mb-2"></i>
            <h6>Book Appointment</h6>
            <button class="btn btn-primary btn-sm" @click="$router.push('/book-appointment')">
              Book Now
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center h-100">
          <div class="card-body">
            <i class="fas fa-user-edit fa-2x text-success mb-2"></i>
            <h6>Update Profile</h6>
            <button class="btn btn-success btn-sm" @click="$router.push('/profile')">
              Update
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center h-100">
          <div class="card-body">
            <i class="fas fa-download fa-2x text-info mb-2"></i>
            <h6>Export History</h6>
            <button class="btn btn-info btn-sm" @click="exportHistory" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin me-1"></i>
              Export CSV
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center h-100">
          <div class="card-body">
            <i class="fas fa-search fa-2x text-warning mb-2"></i>
            <h6>Find Doctors</h6>
            <button class="btn btn-warning btn-sm" @click="activeTab = 'doctors'">
              Search
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Specializations/Departments -->
    <div class="row mb-4">
      <div class="col">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-hospital-symbol"></i> Available Specializations/Departments
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="specialization in specializations" :key="specialization.name" class="col-md-4 mb-3">
                <div class="card border-primary h-100">
                  <div class="card-body text-center">
                    <i class="fas fa-stethoscope fa-2x text-primary mb-2"></i>
                    <h6 class="card-title">{{ specialization.name }}</h6>
                    <p class="card-text small text-muted">{{ specialization.description }}</p>
                    <button 
                      class="btn btn-outline-primary btn-sm"
                      @click="searchDoctorsBySpecialization(specialization.name)"
                    >
                      View Doctors
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="row mb-4">
      <div class="col">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-clock"></i> Upcoming Appointments
            </h5>
          </div>
          <div class="card-body">
            <div v-if="upcomingAppointments.length === 0" class="text-muted text-center py-3">
              No upcoming appointments
            </div>
            <div v-else class="row">
              <div v-for="appointment in upcomingAppointments" :key="appointment.id" class="col-md-4 mb-3">
                <div class="card border-success">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title mb-0">{{ appointment.doctor_name }}</h6>
                      <span class="badge bg-warning">{{ appointment.status }}</span>
                    </div>
                    <p class="card-text">
                      <small class="text-muted">{{ appointment.doctor_specialization }}</small><br>
                      <i class="fas fa-calendar me-2"></i>{{ appointment.date }}<br>
                      <i class="fas fa-clock me-2"></i>{{ appointment.time }}
                    </p>
                    <div class="btn-group btn-group-sm w-100">
                      <button class="btn btn-outline-primary" @click="rescheduleAppointment(appointment)">
                        Reschedule
                      </button>
                      <button class="btn btn-outline-danger" @click="cancelAppointment(appointment.id)">
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="card">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'history' }"
              @click="activeTab = 'history'"
              href="#"
            >
              <i class="fas fa-history"></i> Appointment History
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'treatment' }"
              @click="activeTab = 'treatment'"
              href="#"
            >
              <i class="fas fa-notes-medical"></i> Treatment History
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'doctors' }"
              @click="activeTab = 'doctors'"
              href="#"
            >
              <i class="fas fa-user-md"></i> Find Doctors
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'availability' }"
              @click="activeTab = 'availability'"
              href="#"
            >
              <i class="fas fa-calendar-week"></i> Doctor Availability
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body">
        <!-- Appointment History with Diagnosis & Prescriptions -->
        <div v-if="activeTab === 'history'">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Doctor</th>
                  <th>Specialization</th>
                  <th>Status</th>
                  <th>Diagnosis</th>
                  <th>Prescription</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in appointmentHistory" :key="appointment.id">
                  <td>{{ appointment.date }}</td>
                  <td>{{ appointment.time }}</td>
                  <td>{{ appointment.doctor_name }}</td>
                  <td>{{ appointment.doctor_specialization || 'N/A' }}</td>
                  <td>
                    <span :class="['badge', getStatusBadgeClass(appointment.status)]">
                      {{ appointment.status }}
                    </span>
                  </td>
                  <td>
                    <span v-if="appointment.diagnosis" class="text-success">
                      {{ appointment.diagnosis.substring(0, 50) }}{{ appointment.diagnosis.length > 50 ? '...' : '' }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span v-if="appointment.prescription" class="text-primary">
                      {{ appointment.prescription.substring(0, 30) }}{{ appointment.prescription.length > 30 ? '...' : '' }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm" v-if="appointment.status === 'booked'">
                      <button class="btn btn-outline-primary btn-sm" @click="rescheduleAppointment(appointment)">
                        Reschedule
                      </button>
                      <button class="btn btn-outline-danger btn-sm" @click="cancelAppointment(appointment.id)">
                        Cancel
                      </button>
                    </div>
                    <button v-if="appointment.diagnosis || appointment.prescription" 
                            class="btn btn-info btn-sm"
                            @click="viewDetails(appointment)">
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Treatment History -->
        <div v-if="activeTab === 'treatment'">
          <div v-if="treatmentHistory.length === 0" class="text-muted text-center py-4">
            No treatment history available
          </div>
          <div v-else>
            <div v-for="treatment in treatmentHistory" :key="treatment.id" class="card mb-3">
              <div class="card-body">
                <div class="row">
                  <div class="col-md-3">
                    <strong>Doctor:</strong> {{ treatment.doctor_name }}<br>
                    <strong>Date:</strong> {{ formatDate(treatment.created_at) }}<br>
                    <strong v-if="treatment.follow_up_date">Follow-up:</strong> 
                    <span v-if="treatment.follow_up_date">{{ treatment.follow_up_date }}</span>
                  </div>
                  <div class="col-md-9">
                    <div class="mb-2" v-if="treatment.diagnosis">
                      <strong>Diagnosis:</strong>
                      <p class="mb-1">{{ treatment.diagnosis }}</p>
                    </div>
                    <div class="mb-2" v-if="treatment.prescription">
                      <strong>Prescription:</strong>
                      <p class="mb-1">{{ treatment.prescription }}</p>
                    </div>
                    <div v-if="treatment.summary">
                      <strong>Treatment Summary:</strong>
                      <p class="mt-2">{{ treatment.summary }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Find Doctors -->
        <div v-if="activeTab === 'doctors'">
          <div class="row mb-3">
            <div class="col-md-4">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search doctors..."
                v-model="doctorSearchQuery"
                @input="searchDoctors"
              >
            </div>
            <div class="col-md-3">
              <select class="form-control" v-model="selectedSpecialization" @change="searchDoctors">
                <option value="">All Specializations</option>
                <option v-for="spec in specializations" :key="spec.name" :value="spec.name">
                  {{ spec.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="row">
            <div v-for="doctor in doctors" :key="doctor.id" class="col-md-6 mb-3">
              <div class="card">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="card-title">
                        <i class="fas fa-user-md me-2"></i>{{ doctor.name }}
                      </h6>
                      <p class="card-text">
                        <strong>Specialization:</strong> {{ doctor.specialization || 'General Medicine' }}<br>
                        <strong>Experience:</strong> {{ doctor.experience || 0 }} years<br>
                        <strong>Qualification:</strong> {{ doctor.qualification || 'N/A' }}<br>
                        <strong>Fee:</strong> ₹{{ doctor.consultation_fee || 'Not specified' }}<br>
                        <small class="text-muted">
                          <i class="fas fa-envelope me-1"></i>{{ doctor.email }}<br>
                          <i class="fas fa-phone me-1"></i>{{ doctor.phone || 'N/A' }}
                        </small>
                      </p>
                    </div>
                    <div class="text-end">
                      <button 
                        class="btn btn-outline-info btn-sm mb-2"
                        @click="viewDoctorProfile(doctor.id)"
                      >
                        <i class="fas fa-eye me-1"></i>
                        View Profile
                      </button><br>
                      <button 
                        class="btn btn-primary btn-sm"
                        @click="bookWithDoctor(doctor.id)"
                      >
                        <i class="fas fa-calendar-plus me-1"></i>
                        Book Appointment
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Doctor Availability (7 Days) -->
        <div v-if="activeTab === 'availability'">
          <div class="row mb-3">
            <div class="col-md-4">
              <select class="form-control" v-model="selectedDoctorId" @change="loadDoctorAvailability">
                <option value="">Select a doctor</option>
                <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                  {{ doctor.name }} - {{ doctor.specialization }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="doctorAvailability.length > 0">
            <h6>Next 7 Days Availability</h6>
            <div class="row">
              <div v-for="day in doctorAvailability" :key="day.date" class="col-md-4 mb-3">
                <div class="card" :class="day.is_available ? 'border-success' : 'border-secondary'">
                  <div class="card-body">
                    <h6 class="card-title">
                      {{ day.day_name }}
                      <small class="text-muted">{{ day.date }}</small>
                    </h6>
                    <div v-if="day.is_available && day.availability.length > 0">
                      <div v-for="avail in day.availability" :key="avail.id">
                        <strong>Available:</strong> {{ avail.start_time }} - {{ avail.end_time }}<br>
                        <div v-if="day.booked_times.length > 0" class="mt-2">
                          <small class="text-danger">
                            <strong>Booked:</strong> {{ day.booked_times.join(', ') }}
                          </small>
                        </div>
                      </div>
                      <button 
                        class="btn btn-primary btn-sm mt-2"
                        @click="bookAppointmentForDay(selectedDoctorId, day.date)"
                      >
                        Book for {{ day.day_name }}
                      </button>
                    </div>
                    <div v-else class="text-muted">
                      <i class="fas fa-times-circle me-1"></i>
                      Not Available
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals and other components go here -->

    <!-- Message Alert -->
    <div v-if="message" :class="['alert', 'mt-3', messageType === 'error' ? 'alert-danger' : 'alert-success']">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientDashboard',
  data() {
    return {
      activeTab: 'history',
      upcomingAppointments: [],
      appointmentHistory: [],
      treatmentHistory: [],
      doctors: [],
      specializations: [],
      doctorAvailability: [],
      doctorSearchQuery: '',
      selectedSpecialization: '',
      selectedDoctorId: '',
      message: '',
      messageType: '',
      loading: false
    }
  },

  mounted() {
    this.loadDashboardData()
  },

  methods: {
    async loadDashboardData() {
      try {
        const response = await fetch('/api/patient/dashboard_data', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.upcomingAppointments = data.upcoming_appointments
          this.specializations = data.specializations
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      }

      // Load other data
      this.loadAppointmentHistory()
      this.loadTreatmentHistory()
      this.searchDoctors()
    },

    async loadAppointmentHistory() {
      try {
        const response = await fetch('/api/patient/history', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.appointmentHistory = data.appointments
        }
      } catch (error) {
        console.error('Failed to load appointment history:', error)
      }
    },

    async loadTreatmentHistory() {
      try {
        const response = await fetch('/api/patient/treatment_history', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.treatmentHistory = data.treatments
        }
      } catch (error) {
        console.error('Failed to load treatment history:', error)
      }
    },

    async searchDoctors() {
      try {
        const params = new URLSearchParams()
        if (this.doctorSearchQuery) {
          params.append('search', this.doctorSearchQuery)
        }
        if (this.selectedSpecialization) {
          params.append('specialization', this.selectedSpecialization)
        }

        const response = await fetch(`/api/patient/doctors?${params}`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.doctors = data.doctors
        }
      } catch (error) {
        console.error('Failed to search doctors:', error)
      }
    },

    async loadDoctorAvailability() {
      if (!this.selectedDoctorId) {
        this.doctorAvailability = []
        return
      }

      try {
        const response = await fetch(`/api/patient/doctor/${this.selectedDoctorId}/availability`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.doctorAvailability = data.next_7_days
        }
      } catch (error) {
        console.error('Failed to load doctor availability:', error)
      }
    },

    searchDoctorsBySpecialization(specialization) {
      this.selectedSpecialization = specialization
      this.activeTab = 'doctors'
      this.searchDoctors()
    },

    viewDoctorProfile(doctorId) {
      // Implementation for viewing detailed doctor profile
      this.$router.push({
        name: 'BookAppointment',
        query: { doctor_id: doctorId, view: 'profile' }
      })
    },

    bookWithDoctor(doctorId) {
      this.$router.push({
        name: 'BookAppointment',
        query: { doctor_id: doctorId }
      })
    },

    bookAppointmentForDay(doctorId, date) {
      this.$router.push({
        name: 'BookAppointment',
        query: { doctor_id: doctorId, date: date }
      })
    },

    async exportHistory() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/patient/export_history', {
          method: 'POST',
          credentials: 'include'
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to start export'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    async cancelAppointment(appointmentId) {
      if (!confirm('Are you sure you want to cancel this appointment?')) return

      try {
        const response = await fetch(`/api/patient/cancel/${appointmentId}`, {
          method: 'DELETE',
          credentials: 'include'
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.loadDashboardData()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to cancel appointment'
        this.messageType = 'error'
      }
    },

    rescheduleAppointment(appointment) {
      // Implementation for rescheduling
      console.log('Reschedule appointment:', appointment)
    },

    viewDetails(appointment) {
      // Implementation for viewing full details
      alert(`Diagnosis: ${appointment.diagnosis}

Prescription: ${appointment.prescription}`)
    },

    getStatusBadgeClass(status) {
      const classes = {
        booked: 'bg-warning',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>