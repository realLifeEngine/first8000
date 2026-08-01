/**
 * src/api/branches.js
 * Branch (campus) CRUD — creation/edit restricted to superuser server-side.
 */
import client from './client'

export const listBranches = (params = {}) => client.get('/branches', { params }).then((r) => r.data)
export const createBranch = (payload) => client.post('/branches', payload).then((r) => r.data)
export const updateBranch = (id, payload) => client.put(`/branches/${id}`, payload).then((r) => r.data)
export const deleteBranch = (id) => client.delete(`/branches/${id}`)
