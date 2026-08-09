<template>
  <div>
    <nav class="navbar navbar-dark bg-dark px-4">
      <span class="navbar-brand">Placement Portal — Admin</span>
      <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
    </nav>

    <div class="container mt-4">
      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card text-white bg-primary text-center p-3">
            <h4>{{ stats.total_students }}</h4>
            <p class="mb-0">Students</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-success text-center p-3">
            <h4>{{ stats.total_companies }}</h4>
            <p class="mb-0">Companies</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-warning text-center p-3">
            <h4>{{ stats.total_job_postings }}</h4>
            <p class="mb-0">Job Postings</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-danger text-center p-3">
            <h4>{{ stats.total_applications }}</h4>
            <p class="mb-0">Applications</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'companies' }" @click="tab = 'companies'" href="#">Companies</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'students' }" @click="tab = 'students'" href="#">Students</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'jobs' }" @click="tab = 'jobs'" href="#">Job Postings</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'applications' }" @click="tab = 'applications'" href="#">Applications</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'placement_stats' }" @click="fetchPlacementStats(); tab = 'placement_stats'" href="#">Statistics</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'tasks' }" @click="tab = 'tasks'" href="#">Jobs & Tasks</a>
        </li>
      </ul>

      <!-- Companies Tab -->
      <div v-if="tab === 'companies'">
        <div class="input-group mb-3">
          <input v-model="companySearch" type="text" class="form-control" placeholder="Search by name or industry" />
          <button class="btn btn-outline-secondary" @click="fetchCompanies">Search</button>
        </div>
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>Name</th><th>Industry</th><th>Location</th><th>Status</th><th>Blacklisted</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>{{ c.company_name }}</td>
              <td>{{ c.industry }}</td>
              <td>{{ c.location }}</td>
              <td><span :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span></td>
              <td>{{ c.is_blacklisted ? 'Yes' : 'No' }}</td>
              <td>
                <button class="btn btn-success btn-sm me-1" @click="approveCompany(c.id)">Approve</button>
                <button class="btn btn-danger btn-sm me-1" @click="rejectCompany(c.id)">Reject</button>
                <button class="btn btn-warning btn-sm me-1" @click="blacklistCompany(c.id)">Blacklist</button>
                <button class="btn btn-secondary btn-sm me-1" @click="deactivateCompany(c.id)">Deactivate</button>
                <button class="btn btn-dark btn-sm" @click="removeCompany(c.id)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Students Tab -->
      <div v-if="tab === 'students'">
        <div class="input-group mb-3">
          <input v-model="studentSearch" type="text" class="form-control" placeholder="Search by name, phone or ID" />
          <button class="btn btn-outline-secondary" @click="fetchStudents">Search</button>
        </div>
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>ID</th><th>Name</th><th>Branch</th><th>CGPA</th><th>Blacklisted</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td>{{ s.id }}</td>
              <td>{{ s.full_name }}</td>
              <td>{{ s.branch }}</td>
              <td>{{ s.cgpa }}</td>
              <td>{{ s.is_blacklisted ? 'Yes' : 'No' }}</td>
              <td>
                <button class="btn btn-warning btn-sm me-1" @click="blacklistStudent(s.id)">Blacklist</button>
                <button class="btn btn-danger btn-sm" @click="deactivateStudent(s.id)">Deactivate</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Jobs Tab -->
      <div v-if="tab === 'jobs'">
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="j in jobs" :key="j.id">
              <td>{{ j.job_title }}</td>
              <td>{{ j.company_name }}</td>
              <td>{{ formatDate(j.application_deadline) }}</td>
              <td><span :class="statusBadge(j.status)">{{ j.status }}</span></td>
              <td>
                <button class="btn btn-success btn-sm me-1" @click="approveJob(j.id)">Approve</button>
                <button class="btn btn-danger btn-sm me-1" @click="rejectJob(j.id)">Reject</button>
                <button class="btn btn-dark btn-sm" @click="removeJob(j.id)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Applications Tab -->
      <div v-if="tab === 'applications'">
        <table class="table table-bordered table-hover">
          <thead class="table-dark">
            <tr>
              <th>ID</th><th>Student</th><th>Job Title</th><th>Status</th><th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in applications" :key="a.id">
              <td>{{ a.id }}</td>
              <td>{{ a.student_name }}</td>
              <td>{{ a.job_title }}</td>
              <td><span :class="statusBadge(a.status)">{{ a.status }}</span></td>
              <td>{{ formatDate(a.application_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Statistics Tab -->
      <div v-if="tab === 'placement_stats'">
        <div class="row mb-4">
          <div class="col-md-4 mb-3">
            <div class="card text-center p-3 shadow-sm">
              <h2 class="text-success">{{ placementStats.placement_rate }}%</h2>
              <p class="mb-0">Placement Rate</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="card text-center p-3 shadow-sm">
              <h2 class="text-primary">{{ placementStats.total_selected }}</h2>
              <p class="mb-0">Students Selected</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="card text-center p-3 shadow-sm">
              <h2 class="text-info">{{ placementStats.total_shortlisted }}</h2>
              <p class="mb-0">Students Shortlisted</p>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <div class="card p-3 shadow-sm">
              <h6>Companies</h6>
              <table class="table table-sm mb-0">
                <tr><td>Total</td><td><strong>{{ placementStats.total_companies }}</strong></td></tr>
                <tr><td>Approved</td><td><strong class="text-success">{{ placementStats.approved_companies }}</strong></td></tr>
                <tr><td>Pending</td><td><strong class="text-warning">{{ placementStats.pending_companies }}</strong></td></tr>
              </table>
            </div>
          </div>
          <div class="col-md-6 mb-3">
            <div class="card p-3 shadow-sm">
              <h6>Job Postings</h6>
              <table class="table table-sm mb-0">
                <tr><td>Total</td><td><strong>{{ placementStats.total_jobs }}</strong></td></tr>
                <tr><td>Approved</td><td><strong class="text-success">{{ placementStats.approved_jobs }}</strong></td></tr>
                <tr><td>Pending</td><td><strong class="text-warning">{{ placementStats.pending_jobs }}</strong></td></tr>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks Tab -->
      <div v-if="tab === 'tasks'">
        <div class="row">
          <div class="col-md-4">
            <div class="card p-3 mb-3">
              <h6>Interview Reminders</h6>
              <p class="text-muted small">Send reminders to students about upcoming deadlines.</p>
              <button class="btn btn-primary btn-sm" @click="triggerReminders">Trigger Now</button>
              <p v-if="taskMsg.reminders" class="mt-2 text-success small">{{ taskMsg.reminders }}</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card p-3 mb-3">
              <h6>Monthly Report</h6>
              <p class="text-muted small">Generate and email monthly placement report.</p>
              <button class="btn btn-warning btn-sm" @click="triggerReport">Trigger Now</button>
              <p v-if="taskMsg.report" class="mt-2 text-success small">{{ taskMsg.report }}</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card p-3 mb-3">
              <h6>Export Student CSV</h6>
              <p class="text-muted small">Enter student ID to export their application history.</p>
              <input v-model="exportStudentId" type="number" class="form-control form-control-sm mb-2" placeholder="Student ID" />
              <button class="btn btn-dark btn-sm" @click="triggerExport">Export</button>
              <p v-if="taskMsg.export" class="mt-2 text-success small">{{ taskMsg.export }}</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from '../../api'
export default {
  name: 'AdminDashboard',
  data () {
    return {
      tab: 'companies',
      stats: {},
      placementStats: {},
      companies: [], students: [], jobs: [], applications: [],
      companySearch: '', studentSearch: '',
      exportStudentId: '',
      taskMsg: { reminders: '', report: '', export: '' }
    }
  },
  mounted () {
    this.fetchStats()
    this.fetchCompanies()
    this.fetchStudents()
    this.fetchJobs()
    this.fetchApplications()
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
    async fetchStats () {
      const res = await api.get('/admin/dashboard')
      this.stats = res.data
    },
    async fetchPlacementStats () {
      const res = await api.get('/admin/stats')
      this.placementStats = res.data
    },
    async fetchCompanies () {
      const res = await api.get('/admin/companies', { params: { search: this.companySearch } })
      this.companies = res.data
    },
    async fetchStudents () {
      const res = await api.get('/admin/students', { params: { search: this.studentSearch } })
      this.students = res.data
    },
    async fetchJobs () {
      const res = await api.get('/admin/jobs')
      this.jobs = res.data
    },
    async fetchApplications () {
      const res = await api.get('/admin/applications')
      this.applications = res.data
    },
    async approveCompany (id) {
      await api.patch(`/admin/companies/${id}/approve`)
      this.fetchCompanies()
      this.fetchStats()
    },
    async rejectCompany (id) {
      await api.patch(`/admin/companies/${id}/reject`)
      this.fetchCompanies()
    },
    async blacklistCompany (id) {
      await api.patch(`/admin/companies/${id}/blacklist`)
      this.fetchCompanies()
    },
    async deactivateCompany (id) {
      await api.patch(`/admin/companies/${id}/deactivate`)
      this.fetchCompanies()
    },
    async removeCompany (id) {
      if (confirm('Remove this company?')) {
        await api.delete(`/admin/companies/${id}`)
        this.fetchCompanies()
        this.fetchStats()
      }
    },
    async approveJob (id) {
      await api.patch(`/admin/jobs/${id}/approve`)
      this.fetchJobs()
      this.fetchStats()
    },
    async rejectJob (id) {
      await api.patch(`/admin/jobs/${id}/reject`)
      this.fetchJobs()
    },
    async removeJob (id) {
      if (confirm('Remove this job?')) {
        await api.delete(`/admin/jobs/${id}`)
        this.fetchJobs()
        this.fetchStats()
      }
    },
    async blacklistStudent (id) {
      await api.patch(`/admin/students/${id}/blacklist`)
      this.fetchStudents()
    },
    async deactivateStudent (id) {
      await api.patch(`/admin/students/${id}/deactivate`)
      this.fetchStudents()
    },
    async triggerReminders () {
      const res = await api.post('/admin/trigger/reminders')
      this.taskMsg.reminders = res.data.message
    },
    async triggerReport () {
      const res = await api.post('/admin/trigger/monthly-report')
      this.taskMsg.report = res.data.message
    },
    async triggerExport () {
      const res = await api.post(`/admin/trigger/export/${this.exportStudentId}`)
      this.taskMsg.export = res.data.message
    },
    statusBadge (status) {
      const map = {
        approved: 'badge bg-success',
        pending: 'badge bg-warning text-dark',
        rejected: 'badge bg-danger',
        closed: 'badge bg-secondary',
        applied: 'badge bg-primary',
        shortlisted: 'badge bg-info',
        selected: 'badge bg-success',
        interview: 'badge bg-warning text-dark'
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
