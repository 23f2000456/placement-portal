import { createStore } from 'vuex'

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    email: localStorage.getItem('email') || null
  },
  mutations: {
    SET_AUTH (state, { token, role, email }) {
      state.token = token
      state.role = role
      state.email = email
      localStorage.setItem('token', token)
      localStorage.setItem('role', role)
      localStorage.setItem('email', email)
    },
    CLEAR_AUTH (state) {
      state.token = null
      state.role = null
      state.email = null
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
    }
  },
  actions: {
    login ({ commit }, payload) {
      commit('SET_AUTH', payload)
    },
    logout ({ commit }) {
      commit('CLEAR_AUTH')
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    userRole: state => state.role,
    userEmail: state => state.email,
    token: state => state.token
  }
})