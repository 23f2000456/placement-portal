<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-body p-4">
            <h3 class="card-title text-center mb-4">Placement Portal</h3>
            <h5 class="text-center text-muted mb-4">Register</h5>

            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <div class="mb-3">
              <label class="form-label">Register as</label>
              <select v-model="role" class="form-select">
                <option value="student">Student</option>
                <option value="company">Company</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" placeholder="Enter email" />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" placeholder="Enter password" />
            </div>

            <!-- Student fields -->
            <template v-if="role === 'student'">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="full_name" type="text" class="form-control" placeholder="Full name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Branch</label>
                <input v-model="branch" type="text" class="form-control" placeholder="e.g. CSE" />
              </div>
              <div class="row">
                <div class="col mb-3">
                  <label class="form-label">CGPA</label>
                  <input v-model="cgpa" type="number" step="0.1" class="form-control" placeholder="e.g. 8.5" />
                </div>
                <div class="col mb-3">
                  <label class="form-label">Graduation Year</label>
                  <input v-model="graduation_year" type="number" class="form-control" placeholder="e.g. 2026" />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="phone" type="text" class="form-control" placeholder="Phone number" />
              </div>
            </template>

            <!-- Company fields -->
            <template v-if="role === 'company'">
              <div class="mb-3">
                <label class="form-label">Company Name</label>
                <input v-model="company_name" type="text" class="form-control" placeholder="Company name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Industry</label>
                <input v-model="industry" type="text" class="form-control" placeholder="e.g. IT" />
              </div>
              <div class="mb-3">
                <label class="form-label">Location</label>
                <input v-model="location" type="text" class="form-control" placeholder="e.g. Bangalore" />
              </div>
              <div class="mb-3">
                <label class="form-label">HR Contact</label>
                <input v-model="hr_contact" type="text" class="form-control" placeholder="HR contact name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Website</label>
                <input v-model="website" type="text" class="form-control" placeholder="https://..." />
              </div>
            </template>

            <button class="btn btn-success w-100 mt-2" @click="handleRegister" :disabled="loading">
              {{ loading ? 'Registering...' : 'Register' }}
            </button>
            <hr />
            <p class="text-center mb-0">
              Already have an account?
              <router-link to="/login">Login here</router-link>
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
  name: 'RegisterView',
  data () {
    return {
      role: 'student',
      email: '', password: '',
      full_name: '', branch: '', cgpa: '', graduation_year: '', phone: '',
      company_name: '', industry: '', location: '', hr_contact: '', website: '',
      error: null, success: null, loading: false
    }
  },
  methods: {
    async handleRegister () {
      this.error = null
      this.success = null
      this.loading = true
      try {
        let payload = { email: this.email, password: this.password }
        let endpoint = ''
        if (this.role === 'student') {
          endpoint = '/auth/register/student'
          payload = { ...payload, full_name: this.full_name, branch: this.branch, cgpa: parseFloat(this.cgpa), graduation_year: parseInt(this.graduation_year), phone: this.phone }
        } else {
          endpoint = '/auth/register/company'
          payload = { ...payload, company_name: this.company_name, industry: this.industry, location: this.location, hr_contact: this.hr_contact, website: this.website }
        }
        await api.post(endpoint, payload)
        this.success = this.role === 'student'
          ? 'Student registered successfully! You can now login.'
          : 'Company registered successfully! Awaiting admin approval.'
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
