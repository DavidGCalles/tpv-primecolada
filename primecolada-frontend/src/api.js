import axios from 'axios';
import { auth } from './firebase'; // Importamos la instancia de auth

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// 1. Request Interceptor: Inyección del Token
apiClient.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  
  if (user) {
    try {
      // Obtiene el token JWT actual (refrescándolo si es necesario)
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    } catch (error) {
      console.error("Error obteniendo el token de autenticación:", error);
    }
  } else {
    // Opcional: Manejar el caso donde no hay usuario (ej. endpoints públicos o error de carrera)
    console.warn("Advertencia: Realizando petición sin usuario autenticado.");
  }
  
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 2. Response Interceptor: Manejo Global de Errores (401)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.error("No autorizado (401). El token podría haber expirado o ser inválido.");
      // window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);

export const clientsApi = {
  login: (data) => apiClient.post('/clients/login', data),
};

export const ventasApi = {
  getAll: (clientId = null) => {
    const params = clientId ? { client_id: clientId } : {};
    return apiClient.get('/ventas', { params });
  },
  getById: (id) => apiClient.get(`/ventas/${id}`),
  create: (venta) => apiClient.post('/ventas', venta),
  update: (id, venta) => apiClient.put(`/ventas/${id}`, venta),
  delete: (id) => apiClient.delete(`/ventas/${id}`),
  countByStatus: () => apiClient.get('/ventas/count'),
  getStats: () => apiClient.get('/ventas/stats'),
  getPublicStatus: (id) => apiClient.get(`/public/ventas/${id}`),
};

export const userApi = {
  getProfile: () => apiClient.get('/user/profile'),
};