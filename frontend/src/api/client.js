/**
 * src/api/client.js
 * Central Axios instance for the Kaku CRM API. Attaches the JWT access
 * token to every request, and on a 401 response tries a single silent
 * refresh via /auth/refresh before falling back to logging the user out.
 */
import axios from 'axios'
import router from '../router'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
})

let isRefreshing = false
let pendingQueue = []

function resolveQueue(error, token = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  pendingQueue = []
}

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('kaku_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status

    if (status !== 401 || originalRequest._retry || originalRequest.url?.includes('/auth/login')) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return client(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true
    const refreshToken = localStorage.getItem('kaku_refresh_token')

    if (!refreshToken) {
      isRefreshing = false
      forceLogout()
      return Promise.reject(error)
    }

    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, { refresh_token: refreshToken })
      localStorage.setItem('kaku_access_token', data.access_token)
      resolveQueue(null, data.access_token)
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`
      return client(originalRequest)
    } catch (refreshError) {
      resolveQueue(refreshError, null)
      forceLogout()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

function forceLogout() {
  localStorage.removeItem('kaku_access_token')
  localStorage.removeItem('kaku_refresh_token')
  router.push({ name: 'login' })
}

export default client
