import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (email, password) => api.post('/auth/register', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getCurrentUser: () => api.get('/auth/me'),
};

// Category APIs
export const categoryAPI = {
  getAll: () => api.get('/categories'),
};

// Service APIs
export const serviceAPI = {
  getAll: (categoryId) => api.get('/services', { params: { category_id: categoryId } }),
  getById: (id) => api.get(`/services/${id}`),
};

// Order APIs
export const orderAPI = {
  create: (serviceId, link, quantity) => 
    api.post('/orders', { service_id: serviceId, link, quantity }),
  getAll: () => api.get('/orders'),
  getById: (id) => api.get(`/orders/${id}`),
};

// Payment APIs
export const paymentAPI = {
  createRequest: (paymentMethod, phoneNumber, amount) =>
    api.post('/payments/request', { payment_method: paymentMethod, phone_number: phoneNumber, amount }),
  getAll: () => api.get('/payments'),
};

// Admin APIs
export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  updateUserBalance: (userId, amount) => 
    api.post(`/admin/users/${userId}/balance`, { amount }),
  approvePayment: (paymentId, adminNote) => 
    api.post(`/admin/payments/${paymentId}/approve`, { admin_note: adminNote }),
  rejectPayment: (paymentId, adminNote) => 
    api.post(`/admin/payments/${paymentId}/reject`, { admin_note: adminNote }),
  cancelOrder: (orderId) => api.post(`/admin/orders/${orderId}/cancel`),
  getStats: () => api.get('/admin/stats'),
  getProviders: () => api.get('/admin/providers'),
  createProvider: (data) => api.post('/admin/providers', data),
  createService: (data) => api.post('/admin/services', data),
};

// Config API
export const configAPI = {
  get: () => api.get('/config'),
};

export default api;
