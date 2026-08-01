/**
 * src/api/auth.js
 * Auth endpoints — login, refresh, current-user, password change.
 */
import client from './client'

export function login(username, password) {
  return client.post('/auth/login', { username, password }).then((r) => r.data)
}

export function refresh(refreshToken) {
  return client.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
}

export function fetchMe() {
  return client.get('/auth/me').then((r) => r.data)
}

export function changePassword(oldPassword, newPassword) {
  return client.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword })
}
