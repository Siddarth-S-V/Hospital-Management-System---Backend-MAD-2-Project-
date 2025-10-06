<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary" v-if="user.id">
      <div class="container">
        <a class="navbar-brand" href="#">
          <i class="fas fa-hospital"></i> Medical System
        </a>

        <div class="navbar-nav ms-auto">
          <span class="navbar-text me-3">
            Welcome, {{ user.name }} ({{ user.role }})
          </span>
          <button class="btn btn-outline-light btn-sm" @click="logout">
            <i class="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </div>
    </nav>

    <div class="container-fluid py-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      user: {}
    }
  },

  mounted() {
    this.loadUser()
  },

  methods: {
    loadUser() {
      const userData = localStorage.getItem('user')
      if (userData) {
        this.user = JSON.parse(userData)
      }
    },

    async logout() {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })

        localStorage.removeItem('user')
        this.user = {}
        this.$router.push({ name: 'Login' })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
  },

  watch: {
    '$route'() {
      this.loadUser()
    }
  }
}
</script>

<style>
body {
  background-color: #f8f9fa;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border-radius: 0.375rem;
}

.btn {
  border-radius: 0.375rem;
}

.alert {
  border-radius: 0.375rem;
}
</style>