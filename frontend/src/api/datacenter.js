/**
 * src/api/datacenter.js
 * Data center — revenue/bonus CRUD plus computed reporting endpoints.
 */
import client from './client'

export const listRevenue = (params = {}) => client.get('/data/revenue', { params }).then((r) => r.data)
export const createRevenue = (payload) => client.post('/data/revenue', payload).then((r) => r.data)

export const listBonus = (params = {}) => client.get('/data/bonus', { params }).then((r) => r.data)
export const createBonus = (payload) => client.post('/data/bonus', payload).then((r) => r.data)

export const fetchCampusRanking = () => client.get('/data/ranking').then((r) => r.data)
export const fetchStaffRanking = () => client.get('/data/staff-ranking').then((r) => r.data)
export const fetchBonusSummary = () => client.get('/data/bonus-summary').then((r) => r.data)
