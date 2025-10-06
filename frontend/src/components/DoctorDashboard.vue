<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-user-md"></i> Doctor Dashboard
        </h1>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-calendar fa-2x text-primary mb-2"></i>
            <h5>{{ stats.total_appointments || 0 }}</h5>
            <small class="text-muted">Total Appointments</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-clock fa-2x text-warning mb-2"></i>
            <h5>{{ stats.booked_appointments || 0 }}</h5>
            <small class="text-muted">Upcoming</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
            <h5>{{ stats.completed_appointments || 0 }}</h5>
            <small class="text-muted">Completed</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-users fa-2x text-info mb-2"></i>
            <h5>{{ stats.total_patients || 0 }}</h5>
            <small class="text-muted">Patients</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Tabs -->
    <div class="card">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'appointments' }"
              @click="activeTab = 'appointments'"
              href="#"
            >
              <i class="fas fa-calendar"></i> Appointments
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'availability' }"
              @click="activeTab = 'availability'"
              href="#"
            >
              <i class="fas fa-clock"></i> Availability
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'patients' }"
              @click="activeTab = 'patients'"
              href="#"
            >
              <i class="fas fa-users"></i> Patients
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body">
        <!-- Appointments -->
        <div v-if="activeTab === 'appointments'">
          <div class="row mb-3">
            <div class="col-md-3">
              <select class="form-control" v-model="appointmentFilter" @change="loadAppointments">
                <option value="">All Status</option>
                <option value="booked">Booked</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in appointments" :key="appointment.id">
                  <td>{{ appointment.date }}</td>
                  <td>{{ appointment.time }}</td>
                  <td>{{ appointment.patient_name }}</td>
                  <td>
                    <span :class="['badge', getStatusBadgeClass(appointment.status)]">
                      {{ appointment.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        v-if="appointment.status === 'booked'"
                        class="btn btn-success btn-sm"
                        @click="updateAppointmentStatus(appointment.id, 'completed')"
                      >
                        Complete
                      </button>
                      <button 
                        v-if="appointment.status === 'booked'"
                        class="btn btn-danger btn-sm"
                        @click="updateAppointmentStatus(appointment.id, 'cancelled')"
                      >
                        Cancel
                      </button>
                      <button 
                        v-if="appointment.status === 'completed'"
                        class="btn btn-info btn-sm"
                        @click="showTreatmentModal(appointment)"
                      >
                        Add Treatment
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Availability -->
        <div v-if="activeTab === 'availability'">
          <h5>Set Weekly Availability</h5>
          <form @submit.prevent="saveAvailability">
            <div v-for="(day, index) in weekDays" :key="index" class="row mb-3">
              <div class="col-md-2">
                <label class="form-label">{{ day }}</label>
              </div>
              <div class="col-md-3">
                <input 
                  type="time" 
                  class="form-control" 
                  v-model="availability[index].start_time"
                  placeholder="Start Time"
                >
              </div>
              <div class="col-md-3">
                <input 
                  type="time" 
                  class="form-control" 
                  v-model="availability[index].end_time"
                  placeholder="End Time"
                >
              </div>
              <div class="col-md-2">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary btn-sm"
                  @click="clearDay(index)"
                >
                  Day Off
                </button>
              </div>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
              Save Availability
            </button>
          </form>
        </div>

        <!-- Patients -->
        <div v-if="activeTab === 'patients'">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Total Appointments</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in patients" :key="patient.id">
                  <td>{{ patient.name }}</td>
                  <td>{{ patient.email }}</td>
                  <td>{{ patient.phone || 'N/A' }}</td>
                  <td>{{ getPatientAppointmentCount(patient.id) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Treatment Modal -->
    <div class="modal fade" id="treatmentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Treatment History</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addTreatment">
              <div class="mb-3">
                <label class="form-label">Treatment Summary</label>
                <textarea 
                  class="form-control" 
                  rows="4" 
                  v-model="treatmentData.summary" 
                  required
                  placeholder="Enter treatment details..."
                ></textarea>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  Add Treatment
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
  name: 'DoctorDashboard',
  data() {
    return {
      activeTab: 'appointments',
      stats: {},
      appointments: [],
      patients: [],
      appointmentFilter: '',
      message: '',
      messageType: '',
      loading: false,
      weekDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      availability: Array(7).fill().map((_, index) => ({
        day_of_week: index,
        start_time: '',
        end_time: ''
      })),
      selectedAppointment: null,
      treatmentData: {
        summary: ''
      }
    }
  },

  mounted() {
    this.loadStats()
    this.loadAppointments()
    this.loadPatients()
    this.loadAvailability()
  },

  methods: {
    async loadStats() {
      try {
        const response = await fetch('/api/doctor/stats', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.stats = data.stats
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    },

    async loadAppointments() {
      try {
        const params = new URLSearchParams()
        if (this.appointmentFilter) {
          params.append('status', this.appointmentFilter)
        }

        const response = await fetch(`/api/doctor/appointments?${params}`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.appointments = data.appointments
        }
      } catch (error) {
        console.error('Failed to load appointments:', error)
      }
    },

    async loadPatients() {
      try {
        const response = await fetch('/api/doctor/patients', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.patients = data.patients
        }
      } catch (error) {
        console.error('Failed to load patients:', error)
      }
    },

    async loadAvailability() {
      try {
        const response = await fetch('/api/doctor/availability', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          // Map availability data to form structure
          data.availability.forEach(avail => {
            this.availability[avail.day_of_week] = {
              day_of_week: avail.day_of_week,
              start_time: avail.start_time,
              end_time: avail.end_time
            }
          })
        }
      } catch (error) {
        console.error('Failed to load availability:', error)
      }
    },

    async saveAvailability() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/doctor/availability', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            availability: this.availability
          })
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
        this.message = 'Failed to save availability'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    async updateAppointmentStatus(appointmentId, status) {
      try {
        const response = await fetch(`/api/doctor/appointment/${appointmentId}/status`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ status })
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.loadAppointments()
          this.loadStats()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to update appointment'
        this.messageType = 'error'
      }
    },

    showTreatmentModal(appointment) {
      this.selectedAppointment = appointment
      this.treatmentData.summary = ''
      const modal = new bootstrap.Modal(document.getElementById('treatmentModal'))
      modal.show()
    },

    async addTreatment() {
      this.loading = true

      try {
        const response = await fetch('/api/doctor/history/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            appointment_id: this.selectedAppointment.id,
            summary: this.treatmentData.summary
          })
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.loadAppointments()

          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('treatmentModal'))
          modal.hide()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to add treatment'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    clearDay(index) {
      this.availability[index].start_time = ''
      this.availability[index].end_time = ''
    },

    getStatusBadgeClass(status) {
      const classes = {
        booked: 'bg-warning',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },

    getPatientAppointmentCount(patientId) {
      return this.appointments.filter(app => app.patient_id === patientId).length
    }
  }
}
</script>