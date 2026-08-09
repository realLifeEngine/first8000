/**
 * src/api/students.js
 * Front-desk member management — backs MemberList.vue.
 * Response fields are already camelCase (API uses alias_generator=to_camel).
 */
import client from './client'
import { normalizeListResponse } from './response'

export function listStudents(params = {}) {
  return client.get('/students', { params: { page_size: 100, ...params } }).then((r) => normalizeListResponse(r.data))
}

export function listStudentsPage(params = {}) {
  return client.get('/students', { params }).then((r) => r.data)
}

export function listStudentClassOptions() {
  return client.get('/students/class-options').then((r) => r.data)
}

export function listStudentCounselorOptions() {
  return client.get('/students/counselor-options').then((r) => r.data)
}

export function getStudent(id) {
  return client.get(`/students/${id}`).then((r) => r.data)
}

export function createStudent(payload) {
  return client.post('/students', payload).then((r) => r.data)
}

export function updateStudent(id, payload) {
  return client.put(`/students/${id}`, payload).then((r) => r.data)
}

export function deleteStudent(id) {
  return client.delete(`/students/${id}`)
}

export function listPublicFieldStudents(params = {}) {
  return client.get('/students/public-field', { params: { page_size: 100, ...params } }).then((r) => normalizeListResponse(r.data))
}

export function restorePublicFieldStudent(id) {
  return client.post(`/students/public-field/${id}/restore`).then((r) => r.data)
}
