<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-cogs"></i> Admin Dashboard
        </h1>
      </div>
    </div>

    <!-- Enhanced Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-user-md fa-2x text-success mb-2"></i>
            <h5>{{ stats.total_doctors || 0 }}</h5>
            <small class="text-muted">Doctors</small>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-users fa-2x text-primary mb-2"></i>
            <h5>{{ stats.total_patients || 0 }}</h5>
            <small class="text-muted">Patients</small>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-calendar-check fa-2x text-warning mb-2"></i>
            <h5>{{ stats.booked_appointments || 0 }}</h5>
            <small class="text-muted">Booked</small>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
            <h5>{{ stats.completed_appointments || 0 }}</h5>
            <small class="text-muted">Completed</small>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-calendar-day fa-2x text-info mb-2"></i>
            <h5>{{ stats.todays_appointments || 0 }}</h5>
            <small class="text-muted">Today</small>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-calendar-week fa-2x text-secondary mb-2"></i>
            <h5>{{ stats.weekly_appointments || 0 }}</h5>
            <small class="text-muted">This Week</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Specialization Stats -->
    <div class="row mb-4" v-if="stats.specialization_stats && stats.specialization_stats.length > 0">
      <div class="col">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="fas fa-chart-pie"></i> Doctors by Specialization
            </h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="spec in stats.specialization_stats" :key="spec.specialization" class="col-md-3 mb-2">
                <div class="d-flex justify-content-between">
                  <span class="text-muted">{{ spec.specialization }}</span>
                  <span class="badge bg-primary">{{ spec.count }}</span>
                </div>
              </div>
            </div>
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
              :class="{ active: activeTab === 'users' }"
              @click="activeTab = 'users'"
              href="#"
            >
              <i class="fas fa-users"></i> Manage Users
            </a>
          </li>
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
              :class="{ active: activeTab === 'create' }"
              @click="activeTab = 'create'"
              href="#"
            >
              <i class="fas fa-plus"></i> Create User
            </a>
          </li>
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTab === 'specializations' }"
              @click="activeTab = 'specializations'"
              href="#"
            >
              <i class="fas fa-stethoscope"></i> Specializations
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body">
        <!-- Users Management -->
        <div v-if="activeTab === 'users'">
          <div class="row mb-3">
            <div class="col-md-3">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search users..."
                v-model="searchQuery"
                @input="searchUsers"
              >
            </div>
            <div class="col-md-2">
              <select class="form-control" v-model="roleFilter" @change="searchUsers">
                <option value="">All Roles</option>
                <option value="doctor">Doctors</option>
                <option value="patient">Patients</option>
              </select>
            </div>
            <div class="col-md-3" v-if="roleFilter === 'doctor'">
              <select class="form-control" v-model="specializationFilter" @change="searchUsers">
                <option value="">All Specializations</option>
                <option v-for="spec in specializations" :key="spec.name" :value="spec.name">
                  {{ spec.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Specialization</th>
                  <th>Phone</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.name }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="['badge', user.role === 'doctor' ? 'bg-success' : 'bg-primary']">
                      {{ user.role }}
                    </span>
                  </td>
                  <td>{{ user.specialization || 'N/A' }}</td>
                  <td>{{ user.phone || 'N/A' }}</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="editUser(user)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="deleteUser(user.id)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Appointments -->
        <div v-if="activeTab === 'appointments'">
          <div class="row mb-3">
            <div class="col-md-3">
              <select class="form-control" v-model="appointmentStatusFilter" @change="loadAppointments">
                <option value="">All Status</option>
                <option value="booked">Booked</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="col-md-3">
              <select class="form-control" v-model="appointmentTypeFilter" @change="loadAppointments">
                <option value="">All Appointments</option>
                <option value="upcoming">Upcoming</option>
                <option value="past">Past</option>
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
                  <th>Doctor</th>
                  <th>Specialization</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in appointments" :key="appointment.id">
                  <td>{{ appointment.date }}</td>
                  <td>{{ appointment.time }}</td>
                  <td>{{ appointment.patient_name }}</td>
                  <td>{{ appointment.doctor_name }}</td>
                  <td>{{ appointment.doctor_specialization || 'N/A' }}</td>
                  <td>
                    <span :class="['badge', getStatusBadgeClass(appointment.status)]">
                      {{ appointment.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Create User -->
        <div v-if="activeTab === 'create'">
          <div class="row">
            <div class="col-md-8">
              <form @submit.prevent="createUser">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Name</label>
                      <input type="text" class="form-control" v-model="newUser.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Email</label>
                      <input type="email" class="form-control" v-model="newUser.email" required>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Role</label>
                      <select class="form-control" v-model="newUser.role" required @change="onRoleChange">
                        <option value="">Select Role</option>
                        <option value="doctor">Doctor</option>
                        <option value="patient">Patient</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Phone</label>
                      <input type="tel" class="form-control" v-model="newUser.phone">
                    </div>
                  </div>
                </div>

                <!-- Doctor-specific fields -->
                <div v-if="newUser.role === 'doctor'">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Specialization</label>
                        <select class="form-control" v-model="newUser.specialization">
                          <option value="">Select Specialization</option>
                          <option v-for="spec in specializations" :key="spec.name" :value="spec.name">
                            {{ spec.name }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Experience (Years)</label>
                        <input type="number" class="form-control" v-model="newUser.experience" min="0">
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Qualification</label>
                        <input type="text" class="form-control" v-model="newUser.qualification" placeholder="MBBS, MD, etc.">
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Consultation Fee</label>
                        <input type="number" class="form-control" v-model="newUser.consultation_fee" min="0" step="0.01">
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input type="password" class="form-control" v-model="newUser.password" required>
                </div>

                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  Create User
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- Specializations Management -->
        <div v-if="activeTab === 'specializations'">
          <div class="row mb-4">
            <div class="col-md-6">
              <form @submit.prevent="createSpecialization">
                <div class="mb-3">
                  <label class="form-label">Specialization Name</label>
                  <input type="text" class="form-control" v-model="newSpecialization.name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Description</label>
                  <textarea class="form-control" rows="3" v-model="newSpecialization.description"></textarea>
                </div>
                <button type="submit" class="btn btn-success" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  Add Specialization
                </button>
              </form>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Specialization</th>
                  <th>Description</th>
                  <th>Doctors Count</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="spec in specializations" :key="spec.id">
                  <td><strong>{{ spec.name }}</strong></td>
                  <td>{{ spec.description }}</td>
                  <td>
                    <span class="badge bg-info">
                      {{ getDoctorCountBySpecialization(spec.name) }}
                    </span>
                  </td>
                  <td>{{ formatDate(spec.created_at) }}</td>
                </tr>
              </tbody>
            </table>
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
  name: 'AdminDashboard',
  data() {
    return {
      activeTab: 'users',
      stats: {},
      users: [],
      appointments: [],
      specializations: [],
      searchQuery: '',
      roleFilter: '',
      specializationFilter: '',
      appointmentStatusFilter: '',
      appointmentTypeFilter: '',
      message: '',
      messageType: '',
      loading: false,
      newUser: {
        name: '',
        email: '',
        role: '',
        phone: '',
        password: '',
        specialization: '',
        qualification: '',
        experience: '',
        consultation_fee: ''
      },
      newSpecialization: {
        name: '',
        description: ''
      }
    }
  },

  mounted() {
    this.loadStats()
    this.searchUsers()
    this.loadAppointments()
    this.loadSpecializations()
  },

  methods: {
    async loadStats() {
      try {
        const response = await fetch('/api/admin/stats', {
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

    async loadSpecializations() {
      try {
        const response = await fetch('/api/admin/specializations', {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.specializations = data.specializations
        }
      } catch (error) {
        console.error('Failed to load specializations:', error)
      }
    },

    async searchUsers() {
      try {
        const params = new URLSearchParams({
          q: this.searchQuery,
          role: this.roleFilter,
          specialization: this.specializationFilter
        })

        const response = await fetch(`/api/admin/search?${params}`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.users = data.users
        }
      } catch (error) {
        console.error('Failed to search users:', error)
      }
    },

    async loadAppointments() {
      try {
        const params = new URLSearchParams({
          status: this.appointmentStatusFilter,
          type: this.appointmentTypeFilter
        })

        const response = await fetch(`/api/admin/appointments?${params}`, {
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

    async createUser() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/admin/create_user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.newUser)
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.resetNewUserForm()
          this.searchUsers()
          this.loadStats()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Network error'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    async createSpecialization() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/admin/specializations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.newSpecialization)
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.newSpecialization = { name: '', description: '' }
          this.loadSpecializations()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Network error'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    async deleteUser(userId) {
      if (!confirm('Are you sure you want to delete/blacklist this user?')) return

      try {
        const response = await fetch(`/api/admin/delete_user/${userId}`, {
          method: 'DELETE',
          credentials: 'include'
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'
          this.searchUsers()
          this.loadStats()
        } else {
          this.message = data.error
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Failed to delete user'
        this.messageType = 'error'
      }
    },

    onRoleChange() {
      if (this.newUser.role !== 'doctor') {
        this.newUser.specialization = ''
        this.newUser.qualification = ''
        this.newUser.experience = ''
        this.newUser.consultation_fee = ''
      }
    },

    resetNewUserForm() {
      this.newUser = {
        name: '',
        email: '',
        role: '',
        phone: '',
        password: '',
        specialization: '',
        qualification: '',
        experience: '',
        consultation_fee: ''
      }
    },

    editUser(user) {
      // Implementation for editing user
      console.log('Edit user:', user)
    },

    getStatusBadgeClass(status) {
      const classes = {
        booked: 'bg-warning',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },

    getDoctorCountBySpecialization(specialization) {
      if (!this.stats.specialization_stats) return 0
      const stat = this.stats.specialization_stats.find(s => s.specialization === specialization)
      return stat ? stat.count : 0
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>