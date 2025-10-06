<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card">
        <div class="card-body">
          <div class="text-center mb-4">
            <i class="fas fa-hospital fa-3x text-primary"></i>
            <h2 class="mt-2">Medical System</h2>
            <p class="text-muted">Please sign in to continue</p>
          </div>

          <div v-if="message" :class="['alert', messageType === 'error' ? 'alert-danger' : 'alert-success']">
            {{ message }}
          </div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input 
                type="email" 
                class="form-control" 
                v-model="email" 
                required
                placeholder="Enter your email"
              >
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input 
                type="password" 
                class="form-control" 
                v-model="password" 
                required
                placeholder="Enter your password"
              >
            </div>

            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
              {{ loading ? 'Signing in...' : 'Sign In' }}
            </button>
          </form>

          <div class="mt-4 text-center">
            <small class="text-muted">
              Don't have an account? 
              <a href="#" @click="showRegister = !showRegister" class="text-primary">Register as Patient</a>
            </small>
          </div>

          <!-- Registration Form -->
          <div v-if="showRegister" class="mt-4 pt-4 border-top">
            <h5 class="text-center mb-3">Patient Registration</h5>
            <form @submit.prevent="register">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="registerData.name" 
                  required
                  placeholder="Enter your full name"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="registerData.email" 
                  required
                  placeholder="Enter your email"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="registerData.phone"
                  placeholder="Enter your phone number"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="registerData.password" 
                  required
                  placeholder="Enter your password"
                >
              </div>

              <button type="submit" class="btn btn-success w-100" :disabled="loading">
                <i v-if="loading" class="fas fa-spinner fa-spin me-2"></i>
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </form>
          </div>

          <!-- Default Admin Credentials -->
          <div class="mt-4 p-3 bg-info bg-opacity-10 rounded">
            <small class="text-muted">
              <strong>Default Admin:</strong><br>
              Email: admin@medical.com<br>
              Password: admin123
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      message: '',
      messageType: '',
      loading: false,
      showRegister: false,
      registerData: {
        name: '',
        email: '',
        phone: '',
        password: ''
      }
    }
  },

  methods: {
    async login() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        })

        const data = await response.json()

        if (response.ok) {
          // Store user data
          localStorage.setItem('user', JSON.stringify(data.user))

          // Redirect based on role
          const route = {
            admin: 'AdminDashboard',
            doctor: 'DoctorDashboard',
            patient: 'PatientDashboard'
          }[data.user.role]

          this.$router.push({ name: route })
        } else {
          this.message = data.error || 'Login failed'
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Network error. Please try again.'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },

    async register() {
      this.loading = true
      this.message = ''

      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.registerData)
        })

        const data = await response.json()

        if (response.ok) {
          this.message = 'Registration successful! Please login.'
          this.messageType = 'success'
          this.showRegister = false

          // Clear form
          this.registerData = {
            name: '',
            email: '',
            phone: '',
            password: ''
          }
        } else {
          this.message = data.error || 'Registration failed'
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Network error. Please try again.'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>