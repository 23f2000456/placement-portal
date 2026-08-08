 import axios from 'axios'
import store from './store'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' }
})

// Automatically attach JWT token to every request
api.interceptors.request.use(config => {
  const token = store.getters.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Redirect to login if token expired (401)
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      store.dispatch('logout')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api