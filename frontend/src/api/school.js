/**
 * src/api/school.js
 * Academic affairs — classes, course products, course records/review.
 */
import client from './client'
import { normalizeListResponse } from './response'

export const listClasses = (params = {}) => client.get('/school/classes', { params }).then((r) => normalizeListResponse(r.data))
export const createClass = (payload) => client.post('/school/classes', payload).then((r) => r.data)
export const updateClass = (id, payload) => client.put(`/school/classes/${id}`, payload).then((r) => r.data)
export const deleteClass = (id) => client.delete(`/school/classes/${id}`)
export const listClassStudents = (id) => client.get(`/school/classes/${id}/students`).then((r) => r.data)
export const listAvailableClassStudents = (id) => client.get(`/school/classes/${id}/students/available`).then((r) => r.data)
export const assignStudentToClass = (classId, studentId) => client.post(`/school/classes/${classId}/students/${studentId}`).then((r) => r.data)
export const removeStudentFromClass = (classId, studentId) => client.delete(`/school/classes/${classId}/students/${studentId}`).then((r) => r.data)

export const listCourseProducts = (params = {}) => client.get('/school/course-products', { params }).then((r) => normalizeListResponse(r.data))
export const createCourseProduct = (payload) => client.post('/school/course-products', payload).then((r) => r.data)
export const updateCourseProduct = (id, payload) => client.put(`/school/course-products/${id}`, payload).then((r) => r.data)
export const deleteCourseProduct = (id) => client.delete(`/school/course-products/${id}`)

export const listCourseRecords = (params = {}) => client.get('/school/course-records', { params }).then((r) => r.data)
export const createCourseRecord = (payload) => client.post('/school/course-records', payload).then((r) => r.data)
export const submitCourseReview = (id, payload) => client.patch(`/school/course-records/${id}/review`, payload).then((r) => r.data)

export const listCourseIndexProducts = () => client.get('/school/course-index/products').then((r) => r.data)
export const getCourseIndex = (product, params = {}) => client.get('/school/course-index', { params: { product, ...params } }).then((r) => r.data)
