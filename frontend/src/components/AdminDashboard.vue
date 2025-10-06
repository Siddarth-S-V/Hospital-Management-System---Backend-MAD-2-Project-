<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-cogs"></i> Admin Dashboard
        </h1>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-user-md fa-2x text-success mb-2"></i>
            <h5>{{ stats.total_doctors || 0 }}</h5>
            <small class="text-muted">Doctors</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-users fa-2x text-primary mb-2"></i>
            <h5>{{ stats.total_patients || 0 }}</h5>
            <small class="text-muted">Patients</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="fas fa-calendar-check fa-2x text-warning mb-2"></i>
            <h5>{{ stats.booked_appointments || 0 }}</h5>
            <small class="text-muted">Booked</small>
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
        </ul>
      </div>

      <div class="card-body">
        <!-- Users Management -->
        <div v-if="activeTab === 'users'">
          <div class="row mb-3">
            <div class="col-md-4">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search users..."
                v-model="searchQuery"
                @input="searchUsers"
              >
            </div>
            <div class="col-md-3">
              <select class="form-control" v-model="roleFilter" @change="searchUsers">
                <option value="">All Roles</option>
                <option value="doctor">Doctors</option>
                <option value="patient">Patients</option>
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
                  <td>{{ user.phone || 'N/A' }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteUser(user.id)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Appointments -->
        <div v-if="activeTab === 'appointments'">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appointment in appointments" :key="appointment.id">
                  <td>{{ appointment.date }}</td>
                  <td>{{ appointment.time }}</td>
                  <td>{{ appointment.patient_name }}</td>
                  <td>{{ appointment.doctor_name }}</td>
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
            <div class="col-md-6">
              <form @submit.prevent="createUser">
                <div class="mb-3">
                  <label class="form-label">Name</label>
                  <input type="text" class="form-control" v-model="newUser.name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" v-model="newUser.email" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Role</label>
                  <select class="form-control" v-model="newUser.role" required>
                    <option value="">Select Role</option>
                    <option value="doctor">Doctor</option>
                    <option value="patient">Patient</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">Phone</label>
                  <input type="tel" class="form-control" v-model="newUser.phone">
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
      searchQuery: '',
      roleFilter: '',
      message: '',
      messageType: '',
      loading: false,
      newUser: {
        name: '',
        email: '',
        role: '',
        phone: '',
        password: ''
      }
    }
  },

  mounted() {
    this.loadStats()
    this.searchUsers()
    this.loadAppointments()
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

    async searchUsers() {
      try {
        const params = new URLSearchParams({
          q: this.searchQuery,
          role: this.roleFilter
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
        const response = await fetch('/api/admin/appointments', {
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
          this.newUser = {
            name: '',
            email: '',
            role: '',
            phone: '',
            password: ''
          }
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

    async deleteUser(userId) {
      if (!confirm('Are you sure you want to delete this user?')) return

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