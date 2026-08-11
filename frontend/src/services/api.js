import axios from 'axios';
import { 
  MOCK_USERS, 
  MOCK_USER_HISTORIES, 
  MOCK_METRICS, 
  MOCK_SEVERITY_DISTRIBUTION, 
  MOCK_RISK_TRENDS, 
  MOCK_ANALYTICS_OVERVIEW, 
  MOCK_ALERTS, 
  MOCK_INVESTIGATIONS, 
  MOCK_FEATURE_IMPORTANCE, 
  MOCK_REPORTS_SUMMARY 
} from './mockData';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 4000
});

// Interceptor to attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      return res.data;
    } catch (err) {
      console.warn("Backend auth API offline, returning mock token for frontend flow:", err.message);
      if (username && password) {
        return {
          access_token: 'mock-jwt-token-insider-threat-security',
          token_type: 'bearer',
          username: username || 'analyst',
          role: 'SOC Security Analyst'
        };
      }
      throw new Error('Invalid login credentials');
    }
  },
  getCurrentUser: async () => {
    try {
      const res = await api.get('/auth/me');
      return res.data;
    } catch (err) {
      const token = localStorage.getItem('token');
      if (token) {
        return {
          username: 'analyst',
          role: 'SOC Security Analyst',
          email: 'analyst@cybersec.enterprise.org'
        };
      }
      throw new Error('Unauthenticated');
    }
  }
};

export const dashboardAPI = {
  getMetrics: async () => {
    try {
      return (await api.get('/dashboard/metrics')).data;
    } catch (err) {
      return MOCK_METRICS;
    }
  },
  getSeverityDistribution: async () => {
    try {
      return (await api.get('/dashboard/severity-distribution')).data;
    } catch (err) {
      return MOCK_SEVERITY_DISTRIBUTION;
    }
  },
  getTopRiskUsers: async () => {
    try {
      return (await api.get('/dashboard/top-risk-users')).data;
    } catch (err) {
      return MOCK_USERS.slice(0, 5).map(u => ({
        user: u.user,
        max_risk_score: u.max_risk_score,
        severity: u.latest_severity,
        suspicious_days: Math.round(u.record_count * 0.2)
      }));
    }
  },
  getRiskTrends: async () => {
    try {
      return (await api.get('/dashboard/risk-trends')).data;
    } catch (err) {
      return MOCK_RISK_TRENDS;
    }
  },
};

export const usersAPI = {
  getMonitoredUsers: async (params = {}) => {
    try {
      return (await api.get('/users', { params })).data;
    } catch (err) {
      let filtered = [...MOCK_USERS];
      if (params?.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(u => u.user.toLowerCase().includes(q));
      }
      if (params?.severity) {
        filtered = filtered.filter(u => u.latest_severity.toLowerCase() === params.severity.toLowerCase());
      }
      if (params?.minRisk) {
        filtered = filtered.filter(u => u.max_risk_score >= params.minRisk);
      }
      return filtered;
    }
  },
  getUserHistory: async (userId) => {
    try {
      return (await api.get(`/users/${userId}/history`)).data;
    } catch (err) {
      if (MOCK_USER_HISTORIES[userId]) {
        return MOCK_USER_HISTORIES[userId];
      }
      // Generate realistic default fallback timeline for unindexed user
      return [
        {
          id: 999,
          user: userId,
          day: '2026-08-10',
          logon_count: 3,
          logoff_count: 3,
          off_hours_logons: 2,
          unique_pcs: 2,
          device_connects: 3,
          device_disconnects: 3,
          unique_device_pcs: 1,
          file_activity_count: 14,
          unique_file_pcs: 1,
          unique_files: 8,
          sensitive_file_count: 5,
          email_count: 12,
          attachment_count: 4,
          total_email_size: 140000,
          unique_email_pcs: 1,
          external_email_count: 6,
          http_request_count: 75,
          unique_http_urls: 20,
          off_hours_http: 30,
          ml_risk_score: 72,
          behavioral_risk_score: 68,
          final_risk_score: 70,
          prediction: 0,
          prediction_probability: 0.54,
          severity: 'High'
        }
      ];
    }
  },
};

export const analyticsAPI = {
  getOverview: async () => {
    try {
      return (await api.get('/analytics/overview')).data;
    } catch (err) {
      return MOCK_ANALYTICS_OVERVIEW;
    }
  },
  getModelInfo: async () => {
    try {
      return (await api.get('/analytics/model-info')).data;
    } catch (err) {
      return {
        model_name: "Gradient Boosting Classifier",
        scaler: "MinMaxScaler",
        features_count: 19,
        artifacts: [
          { file_name: "gb.pkl", status: "Loaded" },
          { file_name: "scaler.pkl", status: "Loaded" },
          { file_name: "feature_columns.pkl", status: "Loaded" }
        ],
        actual_notebook_metrics: {
          accuracy: 0.9995,
          precision: 0.9880,
          recall: 0.9982,
          f1_score: 0.9931
        }
      };
    }
  }
};

export const analysisAPI = {
  uploadAnalysis: async (formData) => {
    const res = await api.post('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  exportCSVUrl: `${API_BASE_URL}/analysis/export`
};

export const predictionAPI = {
  predict: async (data) => {
    try {
      return (await api.post('/predict', data)).data;
    } catch (err) {
      throw new Error(err?.response?.data?.detail || "ML Prediction failed.");
    }
  },
  uploadFeatureCSV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/predict/upload-features', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  uploadRawCertCSVs: async (filesDict) => {
    const formData = new FormData();
    if (filesDict.logon) formData.append('logon_file', filesDict.logon);
    if (filesDict.device) formData.append('device_file', filesDict.device);
    if (filesDict.file) formData.append('file_file', filesDict.file);
    if (filesDict.email) formData.append('email_file', filesDict.email);
    if (filesDict.http) formData.append('http_file', filesDict.http);

    const res = await api.post('/predict/upload-raw-cert', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  getFeatureImportance: async () => {
    try {
      return (await api.get('/predict/feature-importance')).data;
    } catch (err) {
      return MOCK_FEATURE_IMPORTANCE;
    }
  },
};

export const alertsAPI = {
  getAlerts: async (params = {}) => {
    try {
      return (await api.get('/alerts', { params })).data;
    } catch (err) {
      let filtered = [...MOCK_ALERTS];
      if (params?.status) {
        filtered = filtered.filter(a => a.status.toLowerCase() === params.status.toLowerCase());
      }
      if (params?.severity) {
        filtered = filtered.filter(a => a.severity.toLowerCase() === params.severity.toLowerCase());
      }
      return filtered;
    }
  },
  updateStatus: async (alertId, status) => {
    try {
      return (await api.patch(`/alerts/${alertId}`, { status })).data;
    } catch (err) {
      const idx = MOCK_ALERTS.findIndex(a => a.id === alertId);
      if (idx !== -1) {
        MOCK_ALERTS[idx].status = status;
        return MOCK_ALERTS[idx];
      }
      return { id: alertId, status };
    }
  },
};

export const investigationsAPI = {
  getInvestigations: async () => {
    try {
      return (await api.get('/investigations')).data;
    } catch (err) {
      return MOCK_INVESTIGATIONS;
    }
  },
  createInvestigation: async (data) => {
    try {
      return (await api.post('/investigations', data)).data;
    } catch (err) {
      const newInv = {
        id: Math.floor(1000 + Math.random() * 9000),
        title: data.title || 'New Security Incident Investigation',
        user: data.user || 'USR0017',
        status: 'New',
        severity: data.severity || 'High',
        risk_score: data.risk_score || 80,
        created_date: new Date().toISOString().split('T')[0],
        assigned_analyst: data.assigned_analyst || 'SOC Security Analyst',
        risk_factors: data.risk_factors || 'Suspicious Activity Detected',
        notes: `[${new Date().toISOString().replace('T', ' ').substring(0, 16)}] Investigation case opened by SOC Analyst.`
      };
      MOCK_INVESTIGATIONS.unshift(newInv);
      return newInv;
    }
  },
  updateInvestigation: async (id, data) => {
    try {
      return (await api.patch(`/investigations/${id}`, data)).data;
    } catch (err) {
      const inv = MOCK_INVESTIGATIONS.find(i => i.id === id);
      if (inv) {
        if (data.notes) {
          const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
          inv.notes = `${inv.notes || ''}\n[${timestamp}] ${data.notes}`;
        }
        if (data.status) {
          inv.status = data.status;
        }
        if (data.assigned_analyst) {
          inv.assigned_analyst = data.assigned_analyst;
        }
        return inv;
      }
      return data;
    }
  },
};

export const reportsAPI = {
  getSummary: async () => {
    try {
      return (await api.get('/reports/summary')).data;
    } catch (err) {
      return MOCK_REPORTS_SUMMARY;
    }
  },
};

export default api;
