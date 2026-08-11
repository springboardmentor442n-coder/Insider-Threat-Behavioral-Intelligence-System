// CERT r4.2 Dataset Mock Engine & Fallback Store

export const MOCK_USERS = [
  {
    user: 'USR0017',
    record_count: 45,
    max_risk_score: 94,
    avg_risk_score: 82.5,
    latest_severity: 'Critical',
    total_off_hours_logons: 38,
    total_device_connects: 42,
    total_sensitive_files: 112,
    total_external_emails: 89,
    last_activity: '2026-08-10T18:45:00Z',
    status: 'Under Investigation'
  },
  {
    user: 'DLM0051',
    record_count: 52,
    max_risk_score: 88,
    avg_risk_score: 76.1,
    latest_severity: 'Critical',
    total_off_hours_logons: 29,
    total_device_connects: 35,
    total_sensitive_files: 94,
    total_external_emails: 64,
    last_activity: '2026-08-10T17:30:00Z',
    status: 'Under Investigation'
  },
  {
    user: 'USR0089',
    record_count: 40,
    max_risk_score: 79,
    avg_risk_score: 64.2,
    latest_severity: 'High',
    total_off_hours_logons: 22,
    total_device_connects: 18,
    total_sensitive_files: 56,
    total_external_emails: 41,
    last_activity: '2026-08-10T16:15:00Z',
    status: 'Monitored'
  },
  {
    user: 'KMC0142',
    record_count: 60,
    max_risk_score: 74,
    avg_risk_score: 58.9,
    latest_severity: 'High',
    total_off_hours_logons: 19,
    total_device_connects: 14,
    total_sensitive_files: 48,
    total_external_emails: 37,
    last_activity: '2026-08-10T15:20:00Z',
    status: 'Monitored'
  },
  {
    user: 'JSS0204',
    record_count: 48,
    max_risk_score: 65,
    avg_risk_score: 42.0,
    latest_severity: 'Medium',
    total_off_hours_logons: 11,
    total_device_connects: 9,
    total_sensitive_files: 22,
    total_external_emails: 19,
    last_activity: '2026-08-10T14:10:00Z',
    status: 'Active'
  },
  {
    user: 'USR0311',
    record_count: 50,
    max_risk_score: 58,
    avg_risk_score: 35.4,
    latest_severity: 'Medium',
    total_off_hours_logons: 8,
    total_device_connects: 6,
    total_sensitive_files: 15,
    total_external_emails: 12,
    last_activity: '2026-08-10T13:45:00Z',
    status: 'Active'
  },
  {
    user: 'RBA0412',
    record_count: 42,
    max_risk_score: 28,
    avg_risk_score: 18.2,
    latest_severity: 'Low',
    total_off_hours_logons: 2,
    total_device_connects: 1,
    total_sensitive_files: 3,
    total_external_emails: 5,
    last_activity: '2026-08-10T12:00:00Z',
    status: 'Active'
  },
  {
    user: 'TMC0501',
    record_count: 55,
    max_risk_score: 15,
    avg_risk_score: 12.1,
    latest_severity: 'Low',
    total_off_hours_logons: 0,
    total_device_connects: 0,
    total_sensitive_files: 1,
    total_external_emails: 2,
    last_activity: '2026-08-10T11:30:00Z',
    status: 'Active'
  }
];

export const MOCK_USER_HISTORIES = {
  'USR0017': [
    {
      id: 101,
      user: 'USR0017',
      day: '2026-08-10',
      logon_count: 6,
      logoff_count: 5,
      off_hours_logons: 5,
      unique_pcs: 3,
      device_connects: 8,
      device_disconnects: 8,
      unique_device_pcs: 2,
      file_activity_count: 38,
      unique_file_pcs: 2,
      unique_files: 24,
      sensitive_file_count: 19,
      email_count: 24,
      attachment_count: 14,
      total_email_size: 480000,
      unique_email_pcs: 2,
      external_email_count: 18,
      http_request_count: 140,
      unique_http_urls: 45,
      off_hours_http: 95,
      ml_risk_score: 96,
      behavioral_risk_score: 92,
      final_risk_score: 94,
      prediction: 1,
      prediction_probability: 0.965,
      severity: 'Critical'
    },
    {
      id: 102,
      user: 'USR0017',
      day: '2026-08-09',
      logon_count: 5,
      logoff_count: 4,
      off_hours_logons: 4,
      unique_pcs: 2,
      device_connects: 6,
      device_disconnects: 6,
      unique_device_pcs: 2,
      file_activity_count: 28,
      unique_file_pcs: 2,
      unique_files: 18,
      sensitive_file_count: 14,
      email_count: 19,
      attachment_count: 10,
      total_email_size: 350000,
      unique_email_pcs: 1,
      external_email_count: 15,
      http_request_count: 110,
      unique_http_urls: 32,
      off_hours_http: 70,
      ml_risk_score: 89,
      behavioral_risk_score: 87,
      final_risk_score: 88,
      prediction: 1,
      prediction_probability: 0.912,
      severity: 'Critical'
    },
    {
      id: 103,
      user: 'USR0017',
      day: '2026-08-08',
      logon_count: 3,
      logoff_count: 3,
      off_hours_logons: 2,
      unique_pcs: 1,
      device_connects: 2,
      device_disconnects: 2,
      unique_device_pcs: 1,
      file_activity_count: 12,
      unique_file_pcs: 1,
      unique_files: 8,
      sensitive_file_count: 4,
      email_count: 10,
      attachment_count: 3,
      total_email_size: 90000,
      unique_email_pcs: 1,
      external_email_count: 5,
      http_request_count: 65,
      unique_http_urls: 18,
      off_hours_http: 25,
      ml_risk_score: 62,
      behavioral_risk_score: 58,
      final_risk_score: 60,
      prediction: 0,
      prediction_probability: 0.48,
      severity: 'Medium'
    }
  ],
  'DLM0051': [
    {
      id: 201,
      user: 'DLM0051',
      day: '2026-08-10',
      logon_count: 4,
      logoff_count: 4,
      off_hours_logons: 4,
      unique_pcs: 2,
      device_connects: 7,
      device_disconnects: 7,
      unique_device_pcs: 1,
      file_activity_count: 30,
      unique_file_pcs: 1,
      unique_files: 20,
      sensitive_file_count: 16,
      email_count: 15,
      attachment_count: 8,
      total_email_size: 280000,
      unique_email_pcs: 1,
      external_email_count: 12,
      http_request_count: 90,
      unique_http_urls: 28,
      off_hours_http: 60,
      ml_risk_score: 90,
      behavioral_risk_score: 86,
      final_risk_score: 88,
      prediction: 1,
      prediction_probability: 0.934,
      severity: 'Critical'
    }
  ]
};

export const MOCK_METRICS = {
  monitored_users: 1000,
  total_records: 330452,
  normal_users_count: 852,
  suspicious_users_count: 112,
  high_risk_users_count: 32,
  critical_users_count: 4,
  total_alerts: 148,
  critical_alerts_count: 18,
  avg_risk_score: 34.8,
  recent_high_risk_activities: [
    { id: 1, user: 'USR0017', action: 'Mass USB Copy of 19 sensitive files', time: '10 mins ago', severity: 'Critical', risk_score: 94 },
    { id: 2, user: 'DLM0051', action: 'Off-hours external email with 8 attachments', time: '42 mins ago', severity: 'Critical', risk_score: 88 },
    { id: 3, user: 'USR0089', action: 'Unusual after-hours HTTP POST requests', time: '2 hours ago', severity: 'High', risk_score: 79 },
    { id: 4, user: 'KMC0142', action: 'Multiple workstation logons detected', time: '4 hours ago', severity: 'High', risk_score: 74 }
  ]
};

export const MOCK_SEVERITY_DISTRIBUTION = {
  Low: 742,
  Medium: 198,
  High: 42,
  Critical: 18
};

export const MOCK_RISK_TRENDS = [
  { day: '08-04', avg_risk_score: 28.4, suspicious_count: 12 },
  { day: '08-05', avg_risk_score: 30.1, suspicious_count: 15 },
  { day: '08-06', avg_risk_score: 31.8, suspicious_count: 19 },
  { day: '08-07', avg_risk_score: 29.5, suspicious_count: 14 },
  { day: '08-08', avg_risk_score: 33.2, suspicious_count: 22 },
  { day: '08-09', avg_risk_score: 36.9, suspicious_count: 28 },
  { day: '08-10', avg_risk_score: 34.8, suspicious_count: 24 }
];

export const MOCK_ANALYTICS_OVERVIEW = {
  logon: {
    regular_hours_logons: 284500,
    off_hours_logons: 45952,
    avg_unique_pcs: 1.4
  },
  device: {
    total_connects: 18420,
    total_disconnects: 18390,
    avg_unique_pcs: 1.1
  },
  file: {
    standard_file_activities: 620400,
    sensitive_file_activities: 38400,
    avg_files_per_day: 12.5
  },
  email: {
    internal_emails: 412000,
    external_emails: 68500,
    attachment_count: 42100,
    total_volume_mb: 18450
  },
  http: {
    total_http_requests: 1850400,
    off_hours_http: 312000,
    unique_urls_visited: 14200
  }
};

export const MOCK_ALERTS = [
  {
    id: 901,
    user: 'USR0017',
    day: '2026-08-10',
    severity: 'Critical',
    risk_score: 94,
    title: 'Exfiltration Warning: High Volume USB File Transfer',
    description: 'User copied 19 classified PDF files to a USB drive during off-hours (22:15).',
    status: 'New',
    detected_time: '2026-08-10T22:15:30Z'
  },
  {
    id: 902,
    user: 'DLM0051',
    day: '2026-08-10',
    severity: 'Critical',
    risk_score: 88,
    title: 'Anomalous External Email Attachment Spurt',
    description: 'User dispatched 8 archive files (.zip) to external Gmail domain.',
    status: 'Investigating',
    detected_time: '2026-08-10T21:40:12Z'
  },
  {
    id: 903,
    user: 'USR0089',
    day: '2026-08-10',
    severity: 'High',
    risk_score: 79,
    title: 'Unusual Off-Hours Web Data Upload',
    description: 'High volume HTTP POST requests to cloud storage domain after 18:00.',
    status: 'Investigating',
    detected_time: '2026-08-10T19:05:00Z'
  },
  {
    id: 904,
    user: 'KMC0142',
    day: '2026-08-09',
    severity: 'High',
    risk_score: 74,
    title: 'Concurrent PC Logon Anomaly',
    description: 'User logged onto 4 distinct workstations within a 30-minute interval.',
    status: 'New',
    detected_time: '2026-08-09T18:22:10Z'
  },
  {
    id: 905,
    user: 'JSS0204',
    day: '2026-08-09',
    severity: 'Medium',
    risk_score: 65,
    title: 'First-time Sensitive File Access',
    description: 'User accessed payroll spreadsheet repository outside normal team scoping.',
    status: 'Resolved',
    detected_time: '2026-08-09T14:12:00Z'
  },
  {
    id: 906,
    user: 'USR0311',
    day: '2026-08-08',
    severity: 'Medium',
    risk_score: 58,
    title: 'After-Hours System Access',
    description: 'System login at 23:45 outside normal employee work shift.',
    status: 'Dismissed',
    detected_time: '2026-08-08T23:45:00Z'
  }
];

export const MOCK_INVESTIGATIONS = [
  {
    id: 501,
    title: 'Project Titan Data Exfiltration Incident',
    user: 'USR0017',
    status: 'Investigating',
    severity: 'Critical',
    risk_score: 94,
    created_date: '2026-08-10',
    assigned_analyst: 'SOC Lead Cyber Analyst',
    risk_factors: 'Off-Hours Logon, USB Device Insertion, Mass Sensitive File Access, External Domain Email',
    notes: '[2026-08-10 22:30] Case opened automatically following Critical Exfiltration Alert #901.\n[2026-08-10 22:45] Confirmed USB drive serial #USB-8841 attached to workstation PC-049.\n[2026-08-10 23:10] Temporarily disabled external USB authorization policy for user USR0017.'
  },
  {
    id: 502,
    title: 'Intellectual Property Transfer via Web Mail',
    user: 'DLM0051',
    status: 'Contained',
    severity: 'Critical',
    risk_score: 88,
    created_date: '2026-08-10',
    assigned_analyst: 'Sr. Forensic Examiner',
    risk_factors: 'External Email Attachment, Compressed Zip Exfiltration, HTTP Cloud Upload',
    notes: '[2026-08-10 21:50] Network DLP caught 8 encrypted zip files sent to non-corporate destination.\n[2026-08-10 22:05] User account suspended pending HR compliance interview.'
  },
  {
    id: 503,
    title: 'Unusual Workstation Credential Spurt',
    user: 'KMC0142',
    status: 'New',
    severity: 'High',
    risk_score: 74,
    created_date: '2026-08-09',
    assigned_analyst: 'Tier 2 Security Analyst',
    risk_factors: 'Multi-PC Logon, After-Hours System Access',
    notes: '[2026-08-09 19:00] Initial triage started. Checking Active Directory kerberos ticket history.'
  }
];

export const MOCK_FEATURE_IMPORTANCE = [
  { feature: 'off_hours_logons', importance: 0.245 },
  { feature: 'sensitive_file_count', importance: 0.198 },
  { feature: 'external_email_count', importance: 0.162 },
  { feature: 'device_connects', importance: 0.125 },
  { feature: 'off_hours_http', importance: 0.089 },
  { feature: 'attachment_count', importance: 0.064 },
  { feature: 'total_email_size', importance: 0.045 },
  { feature: 'unique_pcs', importance: 0.038 },
  { feature: 'unique_files', importance: 0.022 },
  { feature: 'http_request_count', importance: 0.012 }
];

export const MOCK_REPORTS_SUMMARY = {
  generated_at: new Date().toISOString(),
  total_users_monitored: 1000,
  total_behavioral_days_analyzed: 330452,
  normal_records_count: 318500,
  suspicious_records_count: 11952,
  critical_severity_count: 18,
  high_severity_count: 42,
  medium_severity_count: 198,
  low_severity_count: 742,
  top_high_risk_users: [
    { user: 'USR0017', max_score: 94 },
    { user: 'DLM0051', max_score: 88 },
    { user: 'USR0089', max_score: 79 },
    { user: 'KMC0142', max_score: 74 },
    { user: 'JSS0204', max_score: 65 }
  ]
};
