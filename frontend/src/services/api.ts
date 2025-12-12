import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token')
  if (token) {
    // For multipart/form-data, ensure Authorization header is set
    // but don't override Content-Type (axios will set it with boundary)
    if (config.data instanceof FormData) {
      // Remove Content-Type to let axios set it with boundary
      delete config.headers['Content-Type']
    }
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth API
export const authApi = {
  sendOtp: (phone: string) => api.post('/auth/send-otp', { phone }),
  verifyOtp: (phone: string, otp: string) => api.post('/auth/verify-otp', { phone, otp }),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data: { name?: string; email?: string }) => api.put('/auth/profile', data),
}

// Ticket API
export const ticketApi = {
  lookupPnr: (pnr: string) => 
    api.post('/tickets/lookup-pnr', { pnr }),
  uploadImage: (formData: FormData) => {
    // Don't set Content-Type header - axios will set it automatically with boundary
    // The Authorization header from the interceptor will be preserved
    return api.post('/tickets/upload', formData)
  },
  create: (data: any) => api.post('/tickets', data),
  getAll: () => api.get('/tickets'),
  getById: (id: string) => api.get(`/tickets/${id}`),
  update: (id: string, data: any) => api.put(`/tickets/${id}`, data),
  delete: (id: string) => api.delete(`/tickets/${id}`),
}

// Exchange API
export const exchangeApi = {
  findMatches: (ticketId: string, preferences?: any) => 
    api.post(`/exchange/find-matches/${ticketId}`, preferences),
  sendRequest: (data: { targetUserId: string; targetTicketId: string; proposal: any }) =>
    api.post('/exchange/request', data),
  getRequests: () => api.get('/exchange/requests'),
  respondToRequest: (id: string, action: 'accept' | 'decline') =>
    api.post(`/exchange/requests/${id}/${action}`),
  markCompleted: (id: string) => api.post(`/exchange/requests/${id}/complete`),
}

// Chat API
export const chatApi = {
  getMessages: (exchangeId: string) => api.get(`/chat/${exchangeId}`),
  sendMessage: (exchangeId: string, content: string) => 
    api.post(`/chat/${exchangeId}`, { content }),
}

