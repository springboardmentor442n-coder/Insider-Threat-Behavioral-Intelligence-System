import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({ baseURL: BASE, timeout: 30000 });

// ── Request interceptor: attach JWT ──────────────────────────────────────────
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// ── Response interceptor: refresh on 401 ─────────────────────────────────────
api.interceptors.response.use(
  r => r,
  async err => {
    const orig = err.config;
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true;
      const rt = localStorage.getItem('refresh_token');
      if (rt) {
        try {
          const { data } = await axios.post(`${BASE}/auth/refresh?refresh_token=${rt}`);
          localStorage.setItem('access_token', data.access_token);
          orig.headers.Authorization = `Bearer ${data.access_token}`;
          return api(orig);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  login:          (data) => api.post('/auth/login', data),
  register:       (data) => api.post('/auth/register', data),
  me:             ()     => api.get('/auth/me'),
  changePassword: (data) => api.put('/auth/change-password', data),
  logout:         ()     => api.post('/auth/logout'),
};

// ── Employees ─────────────────────────────────────────────────────────────────
export const employeeAPI = {
  list:         (params) => api.get('/employees', { params }),
  get:          (id)     => api.get(`/employees/${id}`),
  create:       (data)   => api.post('/employees', data),
  update:       (id, d)  => api.put(`/employees/${id}`, d),
  terminate:    (id)     => api.delete(`/employees/${id}`),
  departments:  ()       => api.get('/employees/departments'),
  createDept:   (data)   => api.post('/employees/departments', data),
  devices:      (id)     => api.get(`/employees/${id}/devices`),
  addDevice:    (id, d)  => api.post(`/employees/${id}/devices`, d),
};

// ── Activities ────────────────────────────────────────────────────────────────
export const activityAPI = {
  list:         (params)         => api.get('/activities', { params }),
  stats:        (params)         => api.get('/activities/stats/summary', { params }),
  uploadCERT:   (type, file)     => {
    const fd = new FormData(); fd.append('file', file);
    return api.post(`/activities/cert/upload/${type}`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } });
  },
};

// ── Anomalies ─────────────────────────────────────────────────────────────────
export const anomalyAPI = {
  list:     (params) => api.get('/anomalies', { params }),
  detect:   (empId)  => api.post(`/anomalies/detect/${empId}`),
  train:    ()       => api.post('/anomalies/train-model'),
  review:   (id, d)  => api.put(`/anomalies/${id}/review`, d),
};

// ── Risk ──────────────────────────────────────────────────────────────────────
export const riskAPI = {
  score:       (empId)  => api.post(`/risk/score/${empId}`),
  scoreAll:    ()       => api.post('/risk/score-all'),
  leaderboard: (params) => api.get('/risk/leaderboard', { params }),
  history:     (empId, params) => api.get(`/risk/${empId}/history`, { params }),
};

// ── Alerts ────────────────────────────────────────────────────────────────────
export const alertAPI = {
  list:   (params)  => api.get('/alerts', { params }),
  create: (data)    => api.post('/alerts', data),
  update: (id, d)   => api.put(`/alerts/${id}`, d),
};

// ── Incidents ─────────────────────────────────────────────────────────────────
export const incidentAPI = {
  list:     (params) => api.get('/incidents', { params }),
  create:   (data)   => api.post('/incidents', data),
  update:   (id, d)  => api.put(`/incidents/${id}`, d),
  timeline: (id)     => api.get(`/incidents/${id}/timeline`),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardAPI = {
  analyst: () => api.get('/dashboard/security-analyst'),
  soc:     () => api.get('/dashboard/soc'),
  manager: () => api.get('/dashboard/manager'),
};

export default api;
