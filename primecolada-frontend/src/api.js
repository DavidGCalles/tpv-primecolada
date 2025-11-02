import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const clientsApi = {
  login: (telefono) => apiClient.post('/clients/login', { telefono }),
};

export const ventasApi = {
  getAll: (telefono = null) => {
    const params = telefono ? { telefono } : {};
    return apiClient.get('/ventas', { params });
  },
  getById: (id) => apiClient.get(`/ventas/${id}`),
  create: (venta) => apiClient.post('/ventas', venta),
  update: (id, venta) => apiClient.put(`/ventas/${id}`, venta),
  delete: (id) => apiClient.delete(`/ventas/${id}`),
  countByStatus: () => apiClient.get('/ventas/count'),
  getStats: () => apiClient.get('/ventas/stats'),
};
