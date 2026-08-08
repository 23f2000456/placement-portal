<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-body p-4">
            <h3 class="card-title text-center mb-4">Placement Portal</h3>
            <h5 class="text-center text-muted mb-4">Login</h5>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" placeholder="Enter your email" />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" placeholder="Enter your password" />
            </div>
            <button class="btn btn-primary w-100 mt-2" @click="handleLogin" :disabled="loading">
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
            <hr />
            <p class="text-center mb-0">
              Don't have an account?
              <router-link to="/register">Register here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  name: 'LoginView',
  data () {
    return { email: '', password: '', error: null, loading: false }
  },
  methods: {
    async handleLogin () {
      this.error = null
      this.loading = true
      try {
        const response = await api.post('/auth/login', { email: this.email, password: this.password })
        const { access_token, role, email } = response.data
        this.$store.dispatch('login', { token: access_token, role, email })
        if (role === 'admin') this.$router.push('/admin')
        else if (role === 'company') this.$router.push('/company')
        else if (role === 'student') this.$router.push('/student')
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
