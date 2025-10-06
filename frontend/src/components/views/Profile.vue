<template>
  <div>
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3">
          <i class="fas fa-user-edit"></i> Update Profile
        </h1>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <a href="#" @click="goToDashboard">Dashboard</a>
            </li>
            <li class="breadcrumb-item active">Profile</li>
          </ol>
        </nav>
      </div>
    </div>

    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Personal Information</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="profileData.name" 
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="profileData.email" 
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="profileData.phone"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Role</label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="profileData.role" 
                  readonly
                  disabled
                >
                <small class="form-text text-muted">Role cannot be changed</small>
              </div>

              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button 
                  type="button" 
                  class="btn btn-secondary me-md-2"
                  @click="goToDashboard"
                >
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                  {{ loading ? 'Updating...' : 'Update Profile' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Change Password -->
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">Change Password</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordData.current_password" 
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordData.new_password" 
                  required
                  minlength="6"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Confirm New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordData.confirm_password" 
                  required
                  minlength="6"
                >
                <div v-if="passwordData.new_password && passwordData.confirm_password && passwordData.new_password !== passwordData.confirm_password" class="text-danger small mt-1">
                  Passwords do not match
                </div>
              </div>

              <button 
                type="submit" 
                class="btn btn-warning" 
                :disabled="loading || passwordData.new_password !== passwordData.confirm_password"
              >
                <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                {{ loading ? 'Changing...' : 'Change Password' }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="fas fa-info-circle"></i> Profile Information
            </h6>
          </div>
          <div class="card-body">
            <p><strong>Member since:</strong> {{ formatDate(profileData.created_at) }}</p>
            <p><strong>Account type:</strong> 
              <span :class="['badge', getRoleBadgeClass(profileData.role)]">
                {{ profileData.role }}
              </span>
            </p>
            <div class="alert alert-info">
              <small>
                <i class="fas fa-shield-alt me-1"></i>
                Your personal information is secure and encrypted.
              </small>
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
  name: 'Profile',
  data() {
    return {
      profileData: {
        name: '',
        email: '',
        phone: '',
        role: '',
        created_at: ''
      },
      passwordData: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      message: '',
      messageType: '',
      loading: false
    }
  },

  mounted() {
    this.loadProfile()
  },

  methods: {
    loadProfile() {
      const userData = localStorage.getItem('user')
      if (userData) {
        this.profileData = { ...JSON.parse(userData) }
      }
    },

    async updateProfile() {
      this.loading = true
      this.message = ''

      try {
        const endpoint = this.profileData.role === 'patient' 
          ? '/api/patient/update_profile' 
          : `/api/admin/update_user/${this.profileData.id}`

        const response = await fetch(endpoint, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            name: this.profileData.name,
            email: this.profileData.email,
            phone: this.profileData.phone
          })
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'

          // Update local storage
          localStorage.setItem('user', JSON.stringify(data.user))
          this.profileData = { ...data.user }
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
    },

    async changePassword() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/auth/change-password', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            current_password: this.passwordData.current_password,
            new_password: this.passwordData.new_password
          })
        })

        const data = await response.json()

        if (response.ok) {
          this.message = data.message
          this.messageType = 'success'

          // Clear password fields
          this.passwordData = {
            current_password: '',
            new_password: '',
            confirm_password: ''
          }
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
    },

    goToDashboard() {
      const route = {
        admin: 'AdminDashboard',
        doctor: 'DoctorDashboard',
        patient: 'PatientDashboard'
      }[this.profileData.role]

      this.$router.push({ name: route })
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    getRoleBadgeClass(role) {
      const classes = {
        admin: 'bg-danger',
        doctor: 'bg-success',
        patient: 'bg-primary'
      }
      return classes[role] || 'bg-secondary'
    }
  }
}
</script>