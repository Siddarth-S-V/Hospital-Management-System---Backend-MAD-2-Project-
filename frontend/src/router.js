import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import DoctorDashboard from './components/DoctorDashboard.vue'
import PatientDashboard from './components/PatientDashboard.vue'
import BookAppointment from './components/views/BookAppointment.vue'
import Profile from './components/views/Profile.vue'

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/doctor', name: 'DoctorDashboard', component: DoctorDashboard },
  { path: '/patient', name: 'PatientDashboard', component: PatientDashboard },
  { path: '/book-appointment', name: 'BookAppointment', component: BookAppointment },
  { path: '/profile', name: 'Profile', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.name !== 'Login' && !user.id) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router