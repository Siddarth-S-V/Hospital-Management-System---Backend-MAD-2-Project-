<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-calendar-plus"></i> Book Appointment
        </h1>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <a href="#" @click="$router.push('/patient')">Dashboard</a>
            </li>
            <li class="breadcrumb-item active">Book Appointment</li>
          </ol>
        </nav>
      </div>
    </div>

    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Appointment Details</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="bookAppointment">
              <div class="mb-3">
                <label class="form-label">Select Doctor</label>
                <select 
                  class="form-control" 
                  v-model="appointmentData.doctor_id" 
                  required
                  @change="loadDoctorAvailability"
                >
                  <option value="">Choose a doctor...</option>
                  <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                    {{ doctor.name }} - {{ doctor.email }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Appointment Date</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="appointmentData.date" 
                  required
                  :min="minDate"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Appointment Time</label>
                <select class="form-control" v-model="appointmentData.time" required>
                  <option value="">Select time...</option>
                  <option v-for="time in availableTimes" :key="time" :value="time">
                    {{ time }}
                  </option>
                </select>
                <small class="form-text text-muted">
                  Available times based on doctor's schedule
                </small>
              </div>

              <div class="mb-3">
                <label class="form-label">Notes (Optional)</label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="appointmentData.notes"
                  placeholder="Any specific concerns or notes for the doctor..."
                ></textarea>
              </div>

              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button 
                  type="button" 
                  class="btn btn-secondary me-md-2"
                  @click="$router.push('/patient')"
                >
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  {{ loading ? 'Booking...' : 'Book Appointment' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <!-- Doctor Info Card -->
        <div v-if="selectedDoctor" class="card mb-3">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="fas fa-user-md"></i> Doctor Information
            </h6>
          </div>
          <div class="card-body">
            <h6>{{ selectedDoctor.name }}</h6>
            <p class="mb-1">
              <i class="fas fa-envelope me-2"></i>{{ selectedDoctor.email }}
            </p>
            <p class="mb-0">
              <i class="fas fa-phone me-2"></i>{{ selectedDoctor.phone || 'N/A' }}
            </p>
          </div>
        </div>

        <!-- Booking Guidelines -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="fas fa-info-circle"></i> Booking Guidelines
            </h6>
          </div>
          <div class="card-body">
            <ul class="list-unstyled mb-0">
              <li class="mb-2">
                <i class="fas fa-check text-success me-2"></i>
                Appointments can be booked up to 30 days in advance
              </li>
              <li class="mb-2">
                <i class="fas fa-check text-success me-2"></i>
                Please arrive 15 minutes early
              </li>
              <li class="mb-2">
                <i class="fas fa-check text-success me-2"></i>
                Bring your ID and insurance card
              </li>
              <li class="mb-2">
                <i class="fas fa-check text-success me-2"></i>
                Cancel at least 24 hours in advance
              </li>
            </ul>
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
  name: 'BookAppointment',
  data() {
    return {
      doctors: [],
      selectedDoctor: null,
      doctorAvailability: [],
      availableTimes: [],
      appointmentData: {
        doctor_id: '',
        date: '',
        time: '',
        notes: ''
      },
      message: '',
      messageType: '',
      loading: false,
      minDate: ''
    }
  },

  mounted() {
    this.setMinDate()
    this.loadDoctors()

    // Pre-select doctor if passed via route query
    if (this.$route.query.doctor_id) {
      this.appointmentData.doctor_id = parseInt(this.$route.query.doctor_id)
      this.loadDoctorAvailability()
    }
  },

  methods: {
    setMinDate() {
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      this.minDate = tomorrow.toISOString().split('T')[0]
    },

    async loadDoctors() {
      try {
        const response = await fetch('/api/patient/doctors', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.doctors = data.doctors

          // Find selected doctor if pre-selected
          if (this.appointmentData.doctor_id) {
            this.selectedDoctor = this.doctors.find(d => d.id == this.appointmentData.doctor_id)
          }
        }
      } catch (error) {
        console.error('Failed to load doctors:', error)
      }
    },

    async loadDoctorAvailability() {
      if (!this.appointmentData.doctor_id) return

      try {
        // Find selected doctor
        this.selectedDoctor = this.doctors.find(d => d.id == this.appointmentData.doctor_id)

        const response = await fetch(`/api/patient/doctor/${this.appointmentData.doctor_id}/availability`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.doctorAvailability = data.availability
          this.generateAvailableTimes()
        }
      } catch (error) {
        console.error('Failed to load doctor availability:', error)
      }
    },

    generateAvailableTimes() {
      this.availableTimes = []

      if (!this.appointmentData.date || this.doctorAvailability.length === 0) return

      const selectedDate = new Date(this.appointmentData.date)
      const dayOfWeek = selectedDate.getDay() === 0 ? 6 : selectedDate.getDay() - 1 // Convert to 0=Monday

      // Find availability for the selected day
      const dayAvailability = this.doctorAvailability.find(avail => avail.day_of_week === dayOfWeek)

      if (!dayAvailability) return

      // Generate time slots (30-minute intervals)
      const startTime = this.parseTime(dayAvailability.start_time)
      const endTime = this.parseTime(dayAvailability.end_time)

      for (let time = startTime; time < endTime; time += 30) {
        const hours = Math.floor(time / 60)
        const minutes = time % 60
        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
        this.availableTimes.push(timeString)
      }
    },

    parseTime(timeString) {
      const [hours, minutes] = timeString.split(':').map(Number)
      return hours * 60 + minutes
    },

    async bookAppointment() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/patient/book', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.appointmentData)
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'

          // Redirect to dashboard after a delay
          setTimeout(() => {
            this.$router.push('/patient')
          }, 2000)
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Network error. Please try again.'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    }
  },

  watch: {
    'appointmentData.date'() {
      this.appointmentData.time = ''
      this.generateAvailableTimes()
    }
  }
}
</script>