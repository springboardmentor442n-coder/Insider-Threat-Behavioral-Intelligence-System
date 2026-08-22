// ============================================================================
// API CLIENT
// ============================================================================
// One thin wrapper around fetch. Every call goes through here so that auth,
// token refresh, and error handling live in exactly one place.
//
// The token is held in memory and mirrored to localStorage so a refresh of the
// browser tab does not log the analyst out mid-investigation. On a 401 we try
// the refresh token once; if that also fails, we clear and let the app bounce
// to the login screen.

const ACCESS_KEY = 'itbis_access';
const REFRESH_KEY = 'itbis_refresh';

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}
export function setTokens(access, refresh) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}
export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === 'string' ? detail : 'Request failed');
    this.status = status;
    this.detail = detail;
  }
}

async function rawRequest(path, options = {}, useAuth = true) {
  const headers = { ...(options.headers || {}) };
  if (useAuth) {
    const tok = getAccessToken();
    if (tok) headers['Authorization'] = `Bearer ${tok}`;
  }
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(path, { ...options, headers });
  return res;
}

let refreshInFlight = null;

async function tryRefresh() {
  // Collapse concurrent 401s into a single refresh call.
  if (refreshInFlight) return refreshInFlight;
  const refresh = getRefreshToken();
  if (!refresh) return null;

  refreshInFlight = (async () => {
    const res = await rawRequest(
      '/api/auth/refresh',
      { method: 'POST', body: JSON.stringify({ refresh_token: refresh }) },
      false,
    );
    if (!res.ok) { clearTokens(); return null; }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  })();

  const result = await refreshInFlight;
  refreshInFlight = null;
  return result;
}

export async function api(path, options = {}, useAuth = true) {
  let res = await rawRequest(path, options, useAuth);

  if (res.status === 401 && useAuth) {
    const newToken = await tryRefresh();
    if (newToken) {
      res = await rawRequest(path, options, useAuth); // retry once
    }
  }

  if (!res.ok) {
    let detail;
    try { detail = (await res.json()).detail; } catch { detail = res.statusText; }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- typed endpoint helpers -------------------------------------------------

export const auth = {
  // login uses form-encoding (OAuth2PasswordRequestForm), not JSON
  async login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    const res = await rawRequest('/api/auth/login', { method: 'POST', body }, false);
    if (!res.ok) {
      let detail;
      try { detail = (await res.json()).detail; } catch { detail = 'Login failed'; }
      throw new ApiError(res.status, detail);
    }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data;
  },
  me: () => api('/api/auth/me'),
  async logout() {
    const refresh = getRefreshToken();
    try {
      if (refresh) {
        await api('/api/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refresh }),
        });
      }
    } finally {
      clearTokens();
    }
  },
};

export const dashboard = {
  riskTrend: (days = 30) => api(`/api/dashboard/risk-trend?days=${days}`),
  anomalyBreakdown: () => api('/api/dashboard/anomaly-breakdown'),
  topRisks: (limit = 10) => api(`/api/dashboard/top-risks?limit=${limit}`),
};

export const alerts = {
  summary: () => api('/api/alerts/summary'),
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api(`/api/alerts${q ? `?${q}` : ''}`);
  },
  get: (id) => api(`/api/alerts/${id}`),
  acknowledge: (id) => api(`/api/alerts/${id}/acknowledge`, { method: 'POST' }),
  investigate: (id) => api(`/api/alerts/${id}/investigate`, { method: 'POST' }),
  escalate: (id) => api(`/api/alerts/${id}/escalate`, { method: 'POST' }),
  resolve: (id, benign, note) =>
    api(`/api/alerts/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ benign, resolution_note: note || null }),
    }),
};

export const investigate = {
  caseFile: (userId) => api(`/api/investigate/${encodeURIComponent(userId)}`),
  explain: (userId, day) =>
    api(`/api/investigate/${encodeURIComponent(userId)}/explain?day=${day}`),
};

export const reports = {
  catalog: () => api('/api/reports/catalog'),
  // Downloads a report file. Reports are binary (PDF/xlsx), so this bypasses the
  // JSON api() helper: it fetches with the auth token, reads a blob, and triggers
  // a browser download with the server-provided filename.
  download: async (slug, fmt, userId) => {
    const qs = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    const res = await fetch(`/api/reports/${slug}.${fmt}${qs}`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    });
    if (!res.ok) {
      let detail = `Report failed (${res.status})`;
      try { detail = (await res.json()).detail || detail; } catch { /* non-json */ }
      throw new Error(typeof detail === 'string' ? detail : 'Report failed');
    }
    const blob = await res.blob();
    // pull filename out of Content-Disposition, fall back to a sensible default
    const cd = res.headers.get('content-disposition') || '';
    const m = cd.match(/filename="?([^"]+)"?/);
    const filename = m ? m[1] : `${slug}.${fmt}`;
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return filename;
  },
};

export const notifications = {
  list: (unreadOnly = false) =>
    api(`/api/notifications?unread_only=${unreadOnly}`),
  unreadCount: () => api('/api/notifications/unread-count'),
  markRead: (id) => api(`/api/notifications/${id}/read`, { method: 'POST' }),
  markAllRead: () => api('/api/notifications/read-all', { method: 'POST' }),
};

export const entity = {
  analytics: (userId, recentDays = 30) =>
    api(`/api/entity/${encodeURIComponent(userId)}?recent_days=${recentDays}`),
};

export const audit = {
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api(`/api/audit${q ? `?${q}` : ''}`);
  },
  actions: () => api('/api/audit/actions'),
};

export const operators = {
  list: () => api('/api/users'),
};

export const data = {
  stats: () => api('/api/data/stats'),
  employees: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api(`/api/data/employees${q ? `?${q}` : ''}`);
  },
};

export { ApiError };
