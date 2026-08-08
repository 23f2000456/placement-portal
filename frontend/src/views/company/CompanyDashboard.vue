<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-success px-4">
      <span class="navbar-brand">Placement Portal — Company</span>
      <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
    </nav>

    <div class="container mt-4">
      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card text-white bg-primary text-center p-3">
            <h4>{{ stats.total_job_postings }}</h4>
            <p class="mb-0">Job Postings</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-white bg-warning text-center p-3">
            <h4>{{ stats.total_applications }}</h4>
            <p class="mb-0">Total Applications</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-white bg-success text-center p-3">
            <h4>{{ stats.shortlisted_candidates }}</h4>
            <p class="mb-0">Shortlisted</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'jobs' }" @click="tab = 'jobs'" href="#">My Jobs</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'post' }" @click="tab = 'post'" href="#">Post New Job</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'applications' }" @click="tab = 'applications'" href="#">Applications</a>
        </li>
      </ul>

      <!-- My Jobs Tab -->
      <div v-if="tab === 'jobs'">
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>Title</th><th>Deadline</th><th>Status</th><th>Applications</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="j in jobs" :key="j.id">
              <td>{{ j.job_title }}</td>
              <td>{{ j.application_deadline }}</td>
              <td><span :class="statusBadge(j.status)">{{ j.status }}</span></td>
              <td>{{ j.total_applications }}</td>
              <td>
                <button class="btn btn-info btn-sm me-1" @click="viewApplications(j.id)">View Applicants</button>
                <button class="btn btn-danger btn-sm" @click="closeJob(j.id)">Close</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Post New Job Tab -->
      <div v-if="tab === 'post'">
        <div class="card p-4">
          <h5 class="mb-3">Post New Job</h5>
          <div v-if="jobError" class="alert alert-danger">{{ jobError }}</div>
          <div v-if="jobSuccess" class="alert alert-success">{{ jobSuccess }}</div>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Job Title</label>
              <input v-model="newJob.job_title" type="text" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Salary</label>
              <input v-model="newJob.salary" type="number" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Job Description</label>
            <textarea v-model="newJob.job_description" class="form-control" rows="3"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Skills Required</label>
            <input v-model="newJob.skills_required" type="text" class="form-control" placeholder="e.g. Python, Flask" />
          </div>
          <div class="row">
            <div class="col-md-4 mb-3">
              <label class="form-label">Eligible Branches</label>
              <input v-model="newJob.eligible_branches" type="text" class="form-control" placeholder="e.g. CSE,ECE" />
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Minimum CGPA</label>
              <input v-model="newJob.min_cgpa" type="number" step="0.1" class="form-control" />
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Eligible Year</label>
              <input v-model="newJob.eligible_year" type="number" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Application Deadline</label>
            <input v-model="newJob.application_deadline" type="datetime-local" class="form-control" />
          </div>
          <button class="btn btn-success" @click="postJob">Post Job</button>
        </div>
      </div>

      <!-- Applications Tab -->
      <div v-if="tab === 'applications'">
        <div v-if="!selectedJobId" class="alert alert-info">
          Select a job from "My Jobs" tab and click "View Applicants".
        </div>
        <div v-else>
          <button class="btn btn-secondary btn-sm mb-3" @click="selectedJobId = null">← Back</button>
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>Student</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Interview</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in applications" :key="a.application_id">
                <td>{{ a.student_name }}</td>
                <td>{{ a.branch }}</td>
                <td>{{ a.cgpa }}</td>
                <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
                <td>{{ a.interview_datetime || '—' }}</td>
                <td>
                  <select v-model="a.newStatus" class="form-select form-select-sm mb-1">
                    <option value="shortlisted">Shortlisted</option>
                    <option value="interview">Interview</option>
                    <option value="offer">Offer</option>
                    <option value="selected">Selected</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  <input v-model="a.newInterview" type="datetime-local" class="form-control form-control-sm mb-1" />
                  <input v-model="a.newFeedback" type="text" class="form-control form-control-sm mb-1" placeholder="Feedback" />
                  <button class="btn btn-primary btn-sm w-100" @click="updateApplication(a)">Update</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from '../../api'
export default {
  name: 'CompanyDashboard',
  data () {
    return {
      tab: 'jobs',
      stats: {},
      jobs: [],
      applications: [],
      selectedJobId: null,
      jobError: null,
      jobSuccess: null,
      newJob: {
        job_title: '', job_description: '', skills_required: '',
        salary: '', eligible_branches: '', min_cgpa: '',
        eligible_year: '', application_deadline: ''
      }
    }
  },
  mounted () {
    this.fetchStats()
    this.fetchJobs()
  },
  methods: {
    async fetchStats () {
      const res = await api.get('/company/dashboard')
      this.stats = res.data
    },
    async fetchJobs () {
      const res = await api.get('/company/jobs')
      this.jobs = res.data
    },
    async viewApplications (jobId) {
      this.selectedJobId = jobId
      const res = await api.get(`/company/jobs/${jobId}/applications`)
      this.applications = res.data.map(a => ({ ...a, newStatus: a.status, newInterview: '', newFeedback: a.feedback || '' }))
      this.tab = 'applications'
    },
    async closeJob (jobId) {
      if (confirm('Close this job posting?')) {
        await api.patch(`/company/jobs/${jobId}/close`)
        this.fetchJobs()
      }
    },
    async postJob () {
      this.jobError = null
      this.jobSuccess = null
      try {
        const payload = {
          ...this.newJob,
          salary: parseFloat(this.newJob.salary),
          min_cgpa: parseFloat(this.newJob.min_cgpa),
          eligible_year: parseInt(this.newJob.eligible_year),
          application_deadline: new Date(this.newJob.application_deadline).toISOString()
        }
        await api.post('/company/jobs', payload)
        this.jobSuccess = 'Job posted successfully! Awaiting admin approval.'
        this.fetchJobs()
        this.fetchStats()
      } catch (err) {
        this.jobError = err.response?.data?.error || 'Failed to post job.'
      }
    },
    async updateApplication (app) {
      try {
        const payload = { status: app.newStatus, feedback: app.newFeedback }
        if (app.newInterview) payload.interview_datetime = new Date(app.newInterview).toISOString()
        await api.patch(`/company/applications/${app.application_id}/update`, payload)
        this.viewApplications(this.selectedJobId)
      } catch (err) {
        alert(err.response?.data?.error || 'Update failed.')
      }
    },
    statusBadge (status) {
      const map = {
        approved: 'badge bg-success', pending: 'badge bg-warning text-dark',
        rejected: 'badge bg-danger', closed: 'badge bg-secondary',
        applied: 'badge bg-primary', shortlisted: 'badge bg-info',
        selected: 'badge bg-success', interview: 'badge bg-warning text-dark',
        offer: 'badge bg-info'
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
