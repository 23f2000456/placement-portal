<template>
  <div>
    <nav class="navbar navbar-dark bg-primary px-4">
      <span class="navbar-brand">Placement Portal — Student</span>
      <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
    </nav>

    <div class="container mt-4">
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'jobs' }" @click="tab = 'jobs'" href="#">Browse Jobs</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'companies' }" @click="tab = 'companies'; fetchCompanies()" href="#">Companies</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'applications' }" @click="tab = 'applications'" href="#">My Applications</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'history' }" @click="tab = 'history'" href="#">History</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'profile' }" @click="tab = 'profile'" href="#">Profile</a>
        </li>
      </ul>

      <!-- Browse Jobs Tab -->
      <div v-if="tab === 'jobs'">
        <div class="input-group mb-3">
          <input v-model="jobSearch" type="text" class="form-control" placeholder="Search by title or skills" />
          <button class="btn btn-outline-secondary" @click="fetchJobs">Search</button>
        </div>
        <div v-if="applyMsg" class="alert alert-success">{{ applyMsg }}</div>
        <div v-if="applyError" class="alert alert-danger">{{ applyError }}</div>
        <div class="row">
          <div class="col-md-6 mb-3" v-for="j in jobs" :key="j.id">
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <h5 class="card-title">{{ j.job_title }}</h5>
                <h6 class="text-muted">{{ j.company_name }}</h6>
                <p class="card-text small">{{ j.job_description }}</p>
                <ul class="list-unstyled small">
                  <li><strong>Skills:</strong> {{ j.skills_required }}</li>
                  <li><strong>Salary:</strong> ₹{{ j.salary }}</li>
                  <li><strong>Branches:</strong> {{ j.eligible_branches }}</li>
                  <li><strong>Min CGPA:</strong> {{ j.min_cgpa }}</li>
                  <li><strong>Deadline:</strong> {{ formatDate(j.application_deadline) }}</li>
                </ul>
                <button class="btn btn-primary btn-sm w-100" @click="applyJob(j.id)">Apply</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Companies Tab -->
      <div v-if="tab === 'companies'">
        <div class="input-group mb-3">
          <input v-model="companySearch" type="text" class="form-control" placeholder="Search by name or industry" />
          <button class="btn btn-outline-secondary" @click="fetchCompanies">Search</button>
        </div>
        <div class="row">
          <div class="col-md-4 mb-3" v-for="c in companies" :key="c.id">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h5 class="card-title">{{ c.company_name }}</h5>
                <p class="mb-1"><strong>Industry:</strong> {{ c.industry || '—' }}</p>
                <p class="mb-1"><strong>Location:</strong> {{ c.location || '—' }}</p>
                <p class="mb-1">
                  <strong>Website:</strong>
                  <a v-if="c.website" :href="c.website" target="_blank">{{ c.website }}</a>
                  <span v-else>—</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- My Applications Tab -->
      <div v-if="tab === 'applications'">
        <div class="mb-3">
          <button class="btn btn-success btn-sm" @click="triggerExport">Export CSV</button>
          <span v-if="exportMsg" class="ms-3 text-success small">{{ exportMsg }}</span>
        </div>
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>Company</th><th>Job Title</th><th>Status</th><th>Interview</th><th>Feedback</th><th>Applied On</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in applications" :key="a.application_id">
              <td>{{ a.company_name }}</td>
              <td>{{ a.job_title }}</td>
              <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
              <td>{{ formatDate(a.interview_datetime) }}</td>
              <td>{{ a.feedback || '—' }}</td>
              <td>{{ formatDate(a.application_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- History Tab -->
      <div v-if="tab === 'history'">
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>Company</th><th>Job Title</th><th>Salary</th><th>Status</th><th>Applied On</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in history" :key="a.application_id">
              <td>{{ a.company_name }}</td>
              <td>{{ a.job_title }}</td>
              <td>₹{{ a.salary }}</td>
              <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
              <td>{{ formatDate(a.application_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Profile Tab -->
      <div v-if="tab === 'profile'">
        <div class="card p-4 mb-4">
          <h5 class="mb-3">My Profile</h5>
          <div v-if="profileMsg" class="alert alert-success">{{ profileMsg }}</div>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="profile.full_name" type="text" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Phone</label>
              <input v-model="profile.phone" type="text" class="form-control" />
            </div>
          </div>
          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label">Branch</label>
              <input v-model="profile.branch" type="text" class="form-control" />
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">CGPA</label>
              <input v-model="profile.cgpa" type="number" step="0.1" class="form-control" />
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Graduation Year</label>
              <input v-model="profile.graduation_year" type="number" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Skills</label>
            <input v-model="profile.skills" type="text" class="form-control" placeholder="e.g. Python, Flask, Vue" />
          </div>
          <button class="btn btn-primary" @click="updateProfile">Save Profile</button>
        </div>

        <!-- Resume Upload -->
        <div class="card p-4">
          <h5 class="mb-3">Resume</h5>
          <div v-if="resumeMsg" class="alert alert-success">{{ resumeMsg }}</div>
          <div v-if="resumeError" class="alert alert-danger">{{ resumeError }}</div>
          <div v-if="profile.resume_path" class="mb-3">
            <p class="text-muted small">Current resume: <strong>{{ profile.resume_path }}</strong></p>
          </div>
          <div class="mb-3">
            <label class="form-label">Upload Resume (PDF, DOC, DOCX — max 5MB)</label>
            <input type="file" class="form-control" accept=".pdf,.doc,.docx" @change="onFileChange" />
          </div>
          <button class="btn btn-success" @click="uploadResume" :disabled="!resumeFile">Upload Resume</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from '../../api'
export default {
  name: 'StudentDashboard',
  data () {
    return {
      tab: 'jobs',
      jobs: [], applications: [], history: [], companies: [],
      jobSearch: '', companySearch: '',
      profile: {},
      resumeFile: null,
      applyMsg: null, applyError: null,
      profileMsg: null, exportMsg: null,
      resumeMsg: null, resumeError: null
    }
  },
  mounted () {
    this.fetchJobs()
    this.fetchApplications()
    this.fetchHistory()
    this.fetchProfile()
  },
  methods: {
    formatDate (dateStr) {
      if (!dateStr) return '—'
      return new Date(dateStr).toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
        timeZone: 'Asia/Kolkata'
      })
    },
    async fetchJobs () {
      const res = await api.get('/student/jobs', { params: { search: this.jobSearch } })
      this.jobs = res.data
    },
    async fetchCompanies () {
      const res = await api.get('/student/companies', { params: { search: this.companySearch } })
      this.companies = res.data
    },
    async fetchApplications () {
      const res = await api.get('/student/applications')
      this.applications = res.data
    },
    async fetchHistory () {
      const res = await api.get('/student/history')
      this.history = res.data
    },
    async fetchProfile () {
      const res = await api.get('/student/profile')
      this.profile = res.data
    },
    async applyJob (jobId) {
      this.applyMsg = null
      this.applyError = null
      try {
        await api.post(`/student/apply/${jobId}`)
        this.applyMsg = 'Application submitted successfully!'
        this.fetchApplications()
      } catch (err) {
        this.applyError = err.response?.data?.error || 'Failed to apply.'
      }
    },
    async updateProfile () {
      try {
        await api.put('/student/profile', this.profile)
        this.profileMsg = 'Profile updated successfully!'
      } catch (err) {
        alert('Failed to update profile.')
      }
    },
    onFileChange (e) {
      this.resumeFile = e.target.files[0]
    },
    async uploadResume () {
      this.resumeMsg = null
      this.resumeError = null
      try {
        const formData = new FormData()
        formData.append('resume', this.resumeFile)
        await api.post('/student/profile/resume', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.resumeMsg = 'Resume uploaded successfully!'
        this.fetchProfile()
      } catch (err) {
        this.resumeError = err.response?.data?.error || 'Upload failed.'
      }
    },
    async triggerExport () {
      try {
        const res = await api.post('/student/export')
        this.exportMsg = res.data.message
      } catch (err) {
        alert('Export failed.')
      }
    },
    statusBadge (status) {
      const map = {
        applied: 'badge bg-primary',
        shortlisted: 'badge bg-info',
        interview: 'badge bg-warning text-dark',
        offer: 'badge bg-info',
        selected: 'badge bg-success',
        rejected: 'badge bg-danger',
        placed: 'badge bg-success'
      }
      return map[status] || 'badge bg-secondary'
    },
    logout () {
      this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>
