import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('weblock_token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('weblock_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const authAPI = {
  login:  (email, password) => api.post('/auth/login', { email, password }),
  getMe:  ()               => api.get('/auth/me'),
};

// Users
export const usersAPI = {
  list:   (params) => api.get('/users', { params }),
  get:    (id)     => api.get(`/users/${id}`),
  create: (data)   => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id, permanent = false) => api.delete(`/users/${id}`, { params: { permanent } }),
};

// Logs
export const logsAPI = {
  list:   (params) => api.get('/logs', { params }),
  getOne: (id)     => api.get(`/logs/${id}`),
};

// Analytics
export const analyticsAPI = {
  get: (period = '7d') => api.get('/analytics', { params: { period } }),
};

// Locations
export const locationsAPI = {
  list:   ()          => api.get('/locations'),
  create: (data)      => api.post('/locations', data),
  update: (id, data)  => api.put(`/locations/${id}`, data),
};

// Lock simulation
export const lockAPI = {
  requestAccess: (userId, locationId, cardId) => api.post('/lock/access', { userId, locationId, cardId, deviceIp: '192.168.1.100' }),
};

export default api;
