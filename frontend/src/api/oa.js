/**
 * src/api/oa.js
 * Office/OA module — thin wrappers for all 12 OA entities.
 */
import client from './client'
import { normalizeListResponse } from './response'

function makeCrud(path) {
  return {
    list: (params = {}) => client.get(`/oa/${path}`, { params }).then((r) => normalizeListResponse(r.data)),
    create: (payload) => client.post(`/oa/${path}`, payload).then((r) => r.data),
    update: (id, payload) => client.put(`/oa/${path}/${id}`, payload).then((r) => r.data),
    remove: (id) => client.delete(`/oa/${path}/${id}`),
  }
}

export const notices = makeCrud('notices')
export const workPlans = makeCrud('work-plans')
export const workReports = makeCrud('work-reports')
export const contacts = makeCrud('contacts')
export const properties = makeCrud('properties')
export const wages = { list: makeCrud('wages').list, create: makeCrud('wages').create, remove: makeCrud('wages').remove }
export const knowledgeBase = makeCrud('knowledge-base')
export const training = makeCrud('training')
export const documents = { list: makeCrud('documents').list, create: makeCrud('documents').create, remove: makeCrud('documents').remove }
export const messages = { list: makeCrud('messages').list, create: makeCrud('messages').create, remove: makeCrud('messages').remove }
export const operationLogs = { list: makeCrud('operation-logs').list }

export const leaveRequests = {
  ...makeCrud('leave-requests'),
  approve: (id, payload) => client.patch(`/oa/leave-requests/${id}/approve`, payload).then((r) => r.data),
}
