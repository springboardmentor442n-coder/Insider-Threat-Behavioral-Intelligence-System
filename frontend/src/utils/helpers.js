import { format, formatDistanceToNow } from 'date-fns';

// ── Risk helpers ──────────────────────────────────────────────────────────────
export const RISK_COLOR = {
  critical: 'var(--risk-critical)',
  high:     'var(--risk-high)',
  medium:   'var(--risk-medium)',
  low:      'var(--risk-low)',
};

export const SEVERITY_COLOR = {
  critical:      'var(--risk-critical)',
  high:          'var(--risk-high)',
  medium:        'var(--risk-medium)',
  low:           'var(--risk-low)',
  informational: 'var(--risk-info)',
};

export function riskBadge(category) {
  return <span className={`badge badge-${category}`}>{category}</span>;
}

export function severityBadge(severity) {
  return <span className={`badge badge-${severity === 'informational' ? 'info' : severity}`}>{severity}</span>;
}

// ── Date helpers ──────────────────────────────────────────────────────────────
export const fmtDate  = (d) => d ? format(new Date(d), 'MMM d, yyyy') : '—';
export const fmtDT    = (d) => d ? format(new Date(d), 'MMM d, yyyy HH:mm') : '—';
export const fmtAgo   = (d) => d ? formatDistanceToNow(new Date(d), { addSuffix: true }) : '—';
export const fmtTime  = (d) => d ? format(new Date(d), 'HH:mm:ss') : '—';

// ── Number helpers ────────────────────────────────────────────────────────────
export const fmtBytes = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024, sizes = ['B','KB','MB','GB','TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};

export const fmtNum = (n) =>
  n == null ? '—' : new Intl.NumberFormat().format(n);

export const pct = (v, total) =>
  total ? `${((v / total) * 100).toFixed(1)}%` : '0%';

// ── Risk score → color ────────────────────────────────────────────────────────
export function scoreColor(score) {
  if (score >= 75) return 'var(--risk-critical)';
  if (score >= 50) return 'var(--risk-high)';
  if (score >= 25) return 'var(--risk-medium)';
  return 'var(--risk-low)';
}

// ── Activity type labels ──────────────────────────────────────────────────────
export const ACTIVITY_LABELS = {
  login:               'Login',
  logout:              'Logout',
  file_download:       'File Download',
  file_upload:         'File Upload',
  file_delete:         'File Delete',
  email_send:          'Email Send',
  email_receive:       'Email Receive',
  usb_connect:         'USB Connect',
  usb_disconnect:      'USB Disconnect',
  remote_access:       'Remote Access',
  privilege_change:    'Privilege Change',
  data_transfer:       'Data Transfer',
  application_access:  'App Access',
  network_access:      'Network Access',
};

export const ANOMALY_LABELS = {
  unusual_login_time:     'Unusual Login Time',
  abnormal_data_download: 'Abnormal Data Download',
  unauthorized_access:    'Unauthorized Access',
  excessive_file_transfer:'Excessive File Transfer',
  suspicious_device:      'Suspicious Device',
  privilege_abuse:        'Privilege Abuse',
  data_exfiltration:      'Data Exfiltration',
  peer_deviation:         'Peer Deviation',
};

// ── Role labels ───────────────────────────────────────────────────────────────
export const ROLE_LABELS = {
  security_analyst: 'Security Analyst',
  soc_engineer:     'SOC Engineer',
  security_manager: 'Security Manager',
  administrator:    'Administrator',
};

// ── Truncate string ───────────────────────────────────────────────────────────
export const truncate = (str, n = 40) =>
  str && str.length > n ? str.slice(0, n) + '…' : str;

// ── Error extractor ───────────────────────────────────────────────────────────
export const apiError = (e) =>
  e?.response?.data?.detail || e?.message || 'Something went wrong';
