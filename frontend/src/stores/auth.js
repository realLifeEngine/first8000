/**
 * src/stores/auth.js
 * Pinia auth store: holds the JWT access/refresh pair, the current user's
 * profile + resolved effective permissions, and exposes login/logout
 * actions plus permission/role helper getters for use in route guards
 * and component-level UI gating (e.g. v-if="auth.can('student:delete')").
 */
import { defineStore } from 'pinia'
import { login as apiLogin, fetchMe } from '../api/auth'

const ROLE_RANK = { teacher: 0, manager: 1, school_admin: 2, superuser: 3 }

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('kaku_access_token') || null,
    refreshToken: localStorage.getItem('kaku_refresh_token') || null,
    user: null, // { id, username, name, role, branchId, permissions[] }
    ready: false, // true once bootstrap() has resolved
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    role: (state) => state.user?.role || null,
    permissions: (state) => new Set(state.user?.permissions || []),
  },

  actions: {
    can(permissionKey) {
      return this.permissions.has(permissionKey)
    },

    hasRoleAtLeast(minRole) {
      if (!this.role) return false
      return ROLE_RANK[this.role] >= ROLE_RANK[minRole]
    },

    async login(username, password) {
      const tokens = await apiLogin(username, password)
      this.accessToken = tokens.access_token
      this.refreshToken = tokens.refresh_token
      localStorage.setItem('kaku_access_token', tokens.access_token)
      localStorage.setItem('kaku_refresh_token', tokens.refresh_token)
      await this.loadProfile()
    },

    async loadProfile() {
      const profile = await fetchMe()
      this.user = {
        id: profile.id,
        username: profile.username,
        name: profile.name,
        role: profile.role,
        branchId: profile.branch_id,
        permissions: profile.permissions || [],
      }
    },

    async bootstrap() {
      if (this.accessToken) {
        try {
          await this.loadProfile()
        } catch {
          this.logout()
        }
      }
      this.ready = true
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('kaku_access_token')
      localStorage.removeItem('kaku_refresh_token')
    },
  },
})
