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
                <div class="card border-primary">
                  <div class="card-body">
                    <h6 class="card-title">{{ appointment.doctor_name }}</h6>
                    <p class="card-text">
                      <i class="fas fa-calendar me-2"></i>{{ appointment.date }}<br>
                      <i class="fas fa-clock me-2"></i>{{ appointment.time }}
                    </p>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary btn-sm" @click="rescheduleAppointment(appointment)">
                        Reschedule
                      </button>
                      <button class="btn btn-outline-danger btn-sm" @click="cancelAppointment(appointment.id)">
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
        </ul>
      </div>

      <div class="card-body">
        <!-- Appointment History -->
        <div v-if="activeTab === 'history'">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Doctor</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in appointmentHistory" :key="appointment.id">
                  <td>{{ appointment.date }}</td>
                  <td>{{ appointment.time }}</td>
                  <td>{{ appointment.doctor_name }}</td>
                  <td>
                    <span :class="['badge', getStatusBadgeClass(appointment.status)]">
                      {{ appointment.status }}
                    </span>
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
                    <strong>Date:</strong> {{ new Date(treatment.created_at).toLocaleDateString() }}
                  </div>
                  <div class="col-md-9">
                    <strong>Treatment Summary:</strong>
                    <p class="mt-2">{{ treatment.summary }}</p>
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
          </div>

          <div class="row">
            <div v-for="doctor in doctors" :key="doctor.id" class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h6 class="card-title">
                    <i class="fas fa-user-md me-2"></i>{{ doctor.name }}
                  </h6>
                  <p class="card-text">
                    <i class="fas fa-envelope me-2"></i>{{ doctor.email }}<br>
                    <i class="fas fa-phone me-2"></i>{{ doctor.phone || 'N/A' }}
                  </p>
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

    <!-- Reschedule Modal -->
    <div class="modal fade" id="rescheduleModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="confirmReschedule">
              <div class="mb-3">
                <label class="form-label">New Date</label>
                <input type="date" class="form-control" v-model="rescheduleData.date" required>
              </div>
              <div class="mb-3">
                <label class="form-label">New Time</label>
                <input type="time" class="form-control" v-model="rescheduleData.time" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes (Optional)</label>
                <textarea class="form-control" rows="3" v-model="rescheduleData.notes"></textarea>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  Reschedule
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

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
      doctorSearchQuery: '',
      message: '',
      messageType: '',
      loading: false,
      selectedAppointment: null,
      rescheduleData: {
        date: '',
        time: '',
        notes: ''
      }
    }
  },

  mounted() {
    this.loadUpcomingAppointments()
    this.loadAppointmentHistory()
    this.loadTreatmentHistory()
    this.searchDoctors()
  },

  methods: {
    async loadUpcomingAppointments() {
      try {
        const response = await fetch('/api/patient/upcoming_appointments', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.upcomingAppointments = data.appointments
        }
      } catch (error) {
        console.error('Failed to load upcoming appointments:', error)
      }
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
          this.loadUpcomingAppointments()
          this.loadAppointmentHistory()
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
      this.selectedAppointment = appointment
      this.rescheduleData = {
        date: appointment.date,
        time: appointment.time,
        notes: appointment.notes || ''
      }
      const modal = new bootstrap.Modal(document.getElementById('rescheduleModal'))
      modal.show()
    },

    async confirmReschedule() {
      this.loading = true

      try {
        const response = await fetch(`/api/patient/reschedule/${this.selectedAppointment.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.rescheduleData)
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.loadUpcomingAppointments()
          this.loadAppointmentHistory()

          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('rescheduleModal'))
          modal.hide()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to reschedule appointment'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    bookWithDoctor(doctorId) {
      this.$router.push({
        name: 'BookAppointment',
        query: { doctor_id: doctorId }
      })
    },

    getStatusBadgeClass(status) {
      const classes = {
        booked: 'bg-warning',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    }
  }
}
</script>