/**
 * src/api/staff.js
 * Staff (User) management + granular StaffPermission grant/revoke.
 */
import client from './client'

export const listStaff = (params = {}) => client.get('/staff', { params }).then((r) => r.data)
export const getStaff = (id) => client.get(`/staff/${id}`).then((r) => r.data)
export const createStaff = (payload) => client.post('/staff', payload).then((r) => r.data)
export const updateStaff = (id, payload) => client.put(`/staff/${id}`, payload).then((r) => r.data)
export const deleteStaff = (id) => client.delete(`/staff/${id}`)

export const getStaffPermissions = (id) => client.get(`/staff/${id}/permissions`).then((r) => r.data)
export const setStaffPermission = (id, permissionKey, isGranted) =>
  client.post(`/staff/${id}/permissions`, { permission_key: permissionKey, is_granted: isGranted }).then((r) => r.data)
