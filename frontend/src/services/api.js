import axios from 'axios'

const BASE = 'http://localhost:8000'

export const getRoutes = (data) => axios.post(`${BASE}/route`, data)
export const reportIncident = (data) => axios.post(`${BASE}/incident`, data)