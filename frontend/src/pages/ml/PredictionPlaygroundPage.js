import { useState, useRef, useCallback } from 'react';
import AppLayout from '../../components/layout/AppLayout';
import api from '../../api/client';
import {
  FlaskConical, Zap, RotateCcw, Play,
  ShieldAlert, AlertTriangle, CheckCircle, Info,
  Users, ScanLine, ChevronRight, Filter,
  Lock, HardDrive, Mail, User, TrendingUp,
  Clock, Search, X, ExternalLink, UploadCloud,
  FileSpreadsheet, Download, RefreshCw, Layers
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// ─── Feature Schema ───────────────────────────────────────────────────────────
const FEATURE_GROUPS = [
  {
    id: 'login', label: 'Login & Access', icon: Lock, color: '#00d4ff',
    features: [
      { key: 'login_time',      label: 'Login Time (hour)',      min: 0,  max: 23,    step: 1,    default: 9,    hint: 'Average hour user logs in (0–23)' },
      { key: 'failed_logins',   label: 'Failed Logins',          min: 0,  max: 50,    step: 1,    default: 0,    hint: 'Failed login attempts in 30 days' },
      { key: 'vpn_usage',       label: 'VPN Sessions',           min: 0,  max: 200,   step: 1,    default: 0,    hint: 'Remote VPN access sessions' },
      { key: 'login_frequency', label: 'Login Freq. (per day)',  min: 0,  max: 10,    step: 0.1,  default: 1.0,  hint: 'Average logins per day over 30 days' },
    ],
  },
  {
    id: 'file', label: 'File & Data', icon: HardDrive, color: '#f59e0b',
    features: [
      { key: 'file_downloads',    label: 'File Downloads',         min: 0,  max: 500,   step: 1,    default: 10,   hint: 'Files downloaded in 30 days' },
      { key: 'file_uploads',      label: 'File Uploads',           min: 0,  max: 500,   step: 1,    default: 5,    hint: 'Files uploaded in 30 days' },
      { key: 'cloud_uploads',     label: 'Cloud Uploads',          min: 0,  max: 200,   step: 1,    default: 0,    hint: 'Uploads to Drive, Dropbox, S3 etc.' },
      { key: 'usb_usage',         label: 'USB Connections',        min: 0,  max: 50,    step: 1,    default: 0,    hint: 'USB/external device connects' },
      { key: 'data_transfer_size',label: 'Data Transfer (MB)',     min: 0,  max: 10000, step: 10,   default: 50,   hint: 'Total bytes transferred in MB' },
    ],
  },
  {
    id: 'comms', label: 'Comms & Network', icon: Mail, color: '#10b981',
    features: [
      { key: 'email_count',    label: 'Email Count',       min: 0, max: 2000, step: 5,  default: 100, hint: 'Total emails sent + received' },
      { key: 'website_visits', label: 'Website Visits',    min: 0, max: 2000, step: 10, default: 200, hint: 'Web navigation events' },
      { key: 'database_access',label: 'DB Queries',        min: 0, max: 500,  step: 1,  default: 5,   hint: 'Database query event count' },
    ],
  },
  {
    id: 'behavior', label: 'Identity & Behavior', icon: User, color: '#8b5cf6',
    features: [
      { key: 'privilege_escalation',  label: 'Privilege Escalations', min: 0, max: 20,   step: 1,    default: 0,    hint: 'Privilege change events' },
      { key: 'external_storage_usage',label: 'External Storage',       min: 0, max: 50,   step: 1,    default: 0,    hint: 'USB/external drive file write events' },
      { key: 'device_changes',        label: 'Unique Devices',         min: 1, max: 20,   step: 1,    default: 1,    hint: 'Distinct devices accessed' },
      { key: 'working_hours',         label: 'After-Hours Ratio',      min: 0, max: 1,    step: 0.05, default: 0.05, hint: 'Fraction of activity outside 8am–6pm' },
      { key: 'session_duration',      label: 'Avg Session (sec)',       min: 0, max: 7200, step: 60,   default: 300,  hint: 'Average session length in seconds' },
      { key: 'location',              label: 'Location Code',           min: 0, max: 7,    step: 1,    default: 1,    hint: '0=Unknown 1=NY 2=London 3=SF 4=Chicago 5=Tokyo 6=Paris 7=Sydney' },
      { key: 'department',            label: 'Department Code',         min: 0, max: 6,    step: 1,    default: 1,    hint: '0=Other 1=Eng 2=Finance 3=HR 4=Sales 5=Security 6=Legal' },
      { key: 'employee_role',         label: 'Role Code',               min: 0, max: 8,    step: 1,    default: 2,    hint: '0=Other 1=Senior 2=Analyst 3=Manager 4=Director 5=Engineer 6=Counsel 7=Specialist 8=Admin' },
    ],
  },
];

const PRESETS = {
  normal:     { label: 'Normal',    icon: '🟢', color: '#10b981', values: { login_time:9, failed_logins:1, vpn_usage:5, login_frequency:1.2, file_downloads:15, file_uploads:8, cloud_uploads:2, usb_usage:0, data_transfer_size:80, email_count:150, website_visits:300, database_access:3, privilege_escalation:0, external_storage_usage:0, device_changes:1, working_hours:0.04, session_duration:400, location:1, department:1, employee_role:2 } },
  suspicious: { label: 'Suspicious',icon: '🟡', color: '#f59e0b', values: { login_time:22, failed_logins:8, vpn_usage:40, login_frequency:3.5, file_downloads:120, file_uploads:60, cloud_uploads:25, usb_usage:5, data_transfer_size:1500, email_count:600, website_visits:900, database_access:45, privilege_escalation:1, external_storage_usage:4, device_changes:5, working_hours:0.45, session_duration:900, location:2, department:2, employee_role:3 } },
  critical:   { label: 'Critical',  icon: '🔴', color: '#f43f5e', values: { login_time:2, failed_logins:25, vpn_usage:120, login_frequency:7.8, file_downloads:450, file_uploads:380, cloud_uploads:180, usb_usage:22, data_transfer_size:9500, email_count:1800, website_visits:1600, database_access:200, privilege_escalation:8, external_storage_usage:20, device_changes:12, working_hours:0.82, session_duration:6000, location:3, department:5, employee_role:8 } },
};

const LEVEL_META = {
  'Normal':        { color: '#10b981', bg: 'rgba(16,185,129,0.1)',  icon: CheckCircle,  badge: 'NORMAL' },
  'Low Risk':      { color: '#84cc16', bg: 'rgba(132,204,22,0.1)',  icon: Info,         badge: 'LOW RISK' },
  'Medium Risk':   { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)',  icon: AlertTriangle,badge: 'MEDIUM RISK' },
  'High Risk':     { color: '#f97316', bg: 'rgba(249,115,22,0.1)',  icon: ShieldAlert,  badge: 'HIGH RISK' },
  'Critical Risk': { color: '#f43f5e', bg: 'rgba(244,63,94,0.1)',   icon: ShieldAlert,  badge: 'CRITICAL RISK' },
};

function buildDefault() {
  const o = {};
  FEATURE_GROUPS.forEach(g => g.features.forEach(f => { o[f.key] = f.default; }));
  return o;
}

// ─── Shared Components ────────────────────────────────────────────────────────
function LevelBadge({ level, size = 'sm' }) {
  const m = LEVEL_META[level] || LEVEL_META['Normal'];
  const Icon = m.icon;
  const pad = size === 'lg' ? '7px 16px' : '3px 10px';
  const fs  = size === 'lg' ? '0.8rem' : '0.63rem';
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: pad, borderRadius: 20,
      background: m.bg, border: `1px solid ${m.color}50`,
      color: m.color, fontWeight: 800, fontSize: fs, letterSpacing: '0.06em',
    }}>
      <Icon size={size === 'lg' ? 14 : 10} />
      {m.badge}
    </div>
  );
}

function ScoreRing({ score, size = 110 }) {
  const v = Math.min(100, Math.max(0, score));
  const r = (size / 2) - 9;
  const circ = 2 * Math.PI * r;
  const off  = circ - (v / 100) * circ;
  const color = v >= 80 ? '#f43f5e' : v >= 60 ? '#f97316' : v >= 40 ? '#f59e0b' : v >= 20 ? '#84cc16' : '#10b981';
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={8}/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={8}
          strokeDasharray={circ} strokeDashoffset={off} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1)', filter: `drop-shadow(0 0 4px ${color}80)` }}/>
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontSize: size >= 110 ? '1.4rem' : '0.9rem', fontWeight: 900, color, fontFamily: 'var(--font-brand)', lineHeight: 1 }}>
          {v.toFixed(0)}
        </span>
        <span style={{ fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.06em' }}>SCORE</span>
      </div>
    </div>
  );
}

function FeatureSlider({ feature, value, onChange }) {
  const pct = ((value - feature.min) / (feature.max - feature.min)) * 100;
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
        <label title={feature.hint} style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600, cursor: 'help' }}>
          {feature.label}
        </label>
        <input type="number" value={value} min={feature.min} max={feature.max} step={feature.step}
          onChange={e => onChange(feature.key, parseFloat(e.target.value) || 0)}
          style={{ width: 68, textAlign: 'right', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 5, padding: '2px 6px', outline: 'none' }}
        />
      </div>
      <div style={{ position: 'relative', height: 5, borderRadius: 3, background: 'rgba(255,255,255,0.07)' }}>
        <div style={{ height: '100%', borderRadius: 3, background: 'linear-gradient(90deg,#6366f1,#a78bfa)', width: `${Math.min(100, Math.max(0, pct))}%`, transition: 'width 0.1s' }}/>
        <input type="range" min={feature.min} max={feature.max} step={feature.step} value={value}
          onChange={e => onChange(feature.key, parseFloat(e.target.value))}
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer', margin: 0 }}
        />
      </div>
    </div>
  );
}

// ─── Pipeline Result Card ─────────────────────────────────────────────────────
function PipelineResultCard({ emp, rank, onClick, isSelected }) {
  const m = LEVEL_META[emp.threat_level] || LEVEL_META['Normal'];
  return (
    <div
      onClick={() => onClick(emp)}
      style={{
        padding: '14px 16px', borderRadius: 10, cursor: 'pointer',
        background: isSelected ? m.bg : 'rgba(255,255,255,0.03)',
        border: `1px solid ${isSelected ? m.color + '50' : 'rgba(255,255,255,0.07)'}`,
        marginBottom: 8, transition: 'all 0.15s',
        display: 'flex', alignItems: 'center', gap: 12,
      }}
      onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
      onMouseLeave={e => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.03)'; }}
    >
      <div style={{
        width: 28, height: 28, borderRadius: 8, flexShrink: 0,
        background: rank <= 3 ? `${m.color}20` : 'rgba(255,255,255,0.05)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.7rem', fontWeight: 900, color: rank <= 3 ? m.color : 'var(--text-muted)',
      }}>#{rank}</div>
      <div style={{
        width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
        background: `linear-gradient(135deg, ${m.color}40, ${m.color}20)`,
        border: `1px solid ${m.color}40`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.8rem', fontWeight: 800, color: m.color,
      }}>
        {emp.full_name?.charAt(0) || '?'}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {emp.full_name}
        </div>
        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 1 }}>
          {emp.employee_code} · {emp.department}
        </div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div style={{ fontSize: '1.1rem', fontWeight: 900, color: m.color, fontFamily: 'var(--font-brand)', lineHeight: 1 }}>
          {emp.threat_score?.toFixed(1)}
        </div>
        <LevelBadge level={emp.threat_level} />
      </div>
    </div>
  );
}

// ─── Pipeline Detail Panel ────────────────────────────────────────────────────
function PipelineDetailPanel({ emp, onClose }) {
  const m = LEVEL_META[emp.threat_level] || LEVEL_META['Normal'];
  const navigate = useNavigate();
  return (
    <div style={{
      background: 'var(--bg-card)', borderRadius: 16,
      border: `1px solid ${m.color}40`, overflow: 'hidden',
      boxShadow: `0 0 40px ${m.color}15`, animation: 'fadeInUp 0.3s ease-out',
    }}>
      <div style={{ padding: '16px 18px', background: m.bg, borderBottom: `1px solid ${m.color}30`, display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: `${m.color}20`, border: `2px solid ${m.color}60`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', fontWeight: 900, color: m.color }}>
          {emp.full_name?.charAt(0)}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 800, fontSize: '0.9rem', color: '#fff' }}>{emp.full_name}</div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{emp.employee_code} · {emp.designation || 'Staff'} · {emp.department}</div>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {emp.employee_id && (
            <button onClick={() => navigate(`/employees/${emp.employee_id}`)} title="View Profile"
              style={{ padding: '5px 8px', borderRadius: 7, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <ExternalLink size={12}/>
            </button>
          )}
          <button onClick={onClose} style={{ padding: '5px 8px', borderRadius: 7, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={12}/>
          </button>
        </div>
      </div>
      <div style={{ padding: '14px 18px' }}>
        <div style={{
          padding: '8px 12px', borderRadius: 8, marginBottom: 14,
          background: emp.is_insider || emp.threat_score >= 50 ? 'rgba(244,63,94,0.15)' : 'rgba(16,185,129,0.15)',
          border: `1px solid ${emp.is_insider || emp.threat_score >= 50 ? '#f43f5e' : '#10b981'}50`,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{
            fontSize: '0.75rem', fontWeight: 900,
            color: emp.is_insider || emp.threat_score >= 50 ? '#f43f5e' : '#10b981',
            letterSpacing: '0.05em',
          }}>
            {emp.is_insider || emp.threat_score >= 50 ? '🚨 INSIDER THREAT DETECTED' : '🛡️ BENIGN / NORMAL'}
          </div>
          <span style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Classifier Verdict</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
          <ScoreRing score={emp.threat_score} size={90}/>
          <div>
            <LevelBadge level={emp.threat_level} size="lg"/>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 6 }}>
              Confidence: <strong style={{ color: '#fff' }}>{emp.confidence?.toFixed(1)}%</strong>
            </div>
          </div>
        </div>

        {emp.class_probabilities && (
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Class Probabilities</div>
            {Object.entries(emp.class_probabilities).map(([cls, prob]) => {
              const cm = LEVEL_META[cls] || {};
              const pct = Math.round((prob || 0) * 100);
              const isTop = cls === emp.threat_level;
              return (
                <div key={cls} style={{ marginBottom: 5 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', marginBottom: 2 }}>
                    <span style={{ color: isTop ? cm.color : 'var(--text-muted)', fontWeight: isTop ? 700 : 400 }}>{cls}</span>
                    <span style={{ color: cm.color || '#fff', fontWeight: 700 }}>{pct}%</span>
                  </div>
                  <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)' }}>
                    <div style={{ height: '100%', borderRadius: 2, background: cm.color || '#6366f1', width: `${pct}%`, transition: 'width 0.6s', boxShadow: isTop ? `0 0 6px ${cm.color}80` : 'none' }}/>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {emp.top_features?.length > 0 && (
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Top Risk Factors</div>
            {emp.top_features.map((f, i) => (
              <div key={f.feature} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5, padding: '5px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.03)' }}>
                <span style={{ width: 18, height: 18, borderRadius: 4, background: `${m.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.6rem', fontWeight: 800, color: m.color }}>{i+1}</span>
                <span style={{ flex: 1, fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{f.feature.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-primary)' }}>{typeof f.contribution === 'number' ? `${(f.contribution * 100).toFixed(1)}%` : `${f.value}`}</span>
              </div>
            ))}
          </div>
        )}

        {emp.shap_explanation && (
          <div style={{ padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)', marginBottom: 10 }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>AI Explanation</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>{emp.shap_explanation}</div>
          </div>
        )}

        {emp.recommended_action && (
          <div style={{ padding: '8px 12px', borderRadius: 8, background: `${m.color}10`, border: `1px solid ${m.color}30` }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 700, color: m.color, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>⚡ Recommended Action</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-primary)', lineHeight: 1.55, fontWeight: 600 }}>{emp.recommended_action}</div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function PredictionPlaygroundPage() {
  const [mode, setMode]           = useState('pipeline'); // 'pipeline' | 'csv' | 'manual'

  // Pipeline state
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineResult,  setPipelineResult]  = useState(null);
  const [selectedEmp,     setSelectedEmp]     = useState(null);
  const [minLevel,        setMinLevel]        = useState('Normal');
  const [scanDays,        setScanDays]        = useState(30);
  const [searchQ,         setSearchQ]         = useState('');
  const [progressPct,     setProgressPct]     = useState(0);

  // CSV state
  const [csvFile,        setCsvFile]        = useState(null);
  const [csvLoading,     setCsvLoading]     = useState(false);
  const [csvResult,      setCsvResult]      = useState(null);
  const [selectedCsvRow, setSelectedCsvRow] = useState(null);
  const [csvSearch,      setCsvSearch]      = useState('');
  const [csvFilterLevel, setCsvFilterLevel] = useState('All');

  // Manual state
  const [features,      setFeatures]      = useState(buildDefault);
  const [manualResult,  setManualResult]  = useState(null);
  const [manualLoading, setManualLoading] = useState(false);
  const [activeGroup,   setActiveGroup]   = useState('login');
  const [activePreset,  setActivePreset]  = useState(null);
  const resultRef = useRef(null);

  // ── Pipeline ──
  const runPipeline = useCallback(async () => {
    setPipelineLoading(true);
    setPipelineResult(null);
    setSelectedEmp(null);
    setProgressPct(10);

    const prog = setInterval(() => {
      setProgressPct(p => (p >= 90 ? 90 : p + Math.floor(Math.random() * 8) + 2));
    }, 600);

    try {
      const { data } = await api.get(
        `/ml/pipeline/scan?min_level=${encodeURIComponent(minLevel)}&days=${scanDays}&limit=300`,
        { timeout: 120000 }  // 120s — pipeline scans up to 300 employees synchronously
      );
      clearInterval(prog);
      setProgressPct(100);
      setPipelineResult(data);
      setPipelineLoading(false);
      if (data.total_scanned === 0) {
        toast.error('No employees found in database. Click Re-Seed 300 Cohort to populate the DB.', { duration: 6000 });
      } else if (data.total_flagged === 0) {
        toast('Scan complete — all employees scored Normal at this sensitivity level.', { icon: '✅' });
      } else {
        toast.success(`Scan complete — ${data.total_flagged} employee(s) flagged from ${data.total_scanned} scanned.`);
      }
    } catch (e) {
      clearInterval(prog);
      toast.error(`Pipeline scan failed: ${e.response?.data?.detail || e.message}`);
      setPipelineLoading(false);
      setProgressPct(0);
    }
  }, [minLevel, scanDays]);

  // ── CSV Actions ──
  const handleCsvUpload = async () => {
    if (!csvFile) {
      toast.error('Please select or drag a CSV file first.');
      return;
    }
    setCsvLoading(true);
    setCsvResult(null);
    setSelectedCsvRow(null);

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const { data } = await api.post('/ml/predict-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCsvResult(data);
      setCsvLoading(false);
      setCsvFilterLevel('All');
      setCsvSearch('');
      toast.success(`Predictions complete for ${data.total_rows} CSV rows!`);
    } catch (e) {
      setCsvLoading(false);
      toast.error(`CSV prediction failed: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleDownloadSampleCsv = () => {
    window.open(`${BASE_URL}/ml/download-sample-csv`, '_blank');
    toast.success('Downloading 50-row synthetic CSV sample...');
  };

  const handleReSeedSynthetic300 = async () => {
    try {
      toast.loading('Re-seeding 300 synthetic cohort database...', { id: 'seed-toast' });
      await api.post('/ml/seed-synthetic-300');
      toast.success('Database successfully re-seeded with 300 synthetic employees!', { id: 'seed-toast' });
      if (mode === 'pipeline') runPipeline();
    } catch (e) {
      toast.error(`Seeding failed: ${e.response?.data?.detail || e.message}`, { id: 'seed-toast' });
    }
  };

  // ── Manual ──
  const handleChange = (key, val) => { setFeatures(p => ({ ...p, [key]: val })); setActivePreset(null); };
  const applyPreset  = (name) => { setFeatures({ ...buildDefault(), ...PRESETS[name].values }); setActivePreset(name); toast.success(`Preset: ${PRESETS[name].label}`); };

  const runManual = async () => {
    setManualLoading(true); setManualResult(null);
    try {
      const { data } = await api.post('/ml/predict/manual', features);
      setManualResult(data);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
      toast.success('Prediction complete!');
    } catch (e) { toast.error(`Failed: ${e.response?.data?.detail || e.message}`); }
    finally { setManualLoading(false); }
  };

  const currentGroup = FEATURE_GROUPS.find(g => g.id === activeGroup);

  const filteredResults = pipelineResult?.results?.filter(e =>
    !searchQ || e.full_name?.toLowerCase().includes(searchQ.toLowerCase()) ||
    e.employee_code?.toLowerCase().includes(searchQ.toLowerCase()) ||
    e.department?.toLowerCase().includes(searchQ.toLowerCase())
  ) || [];

  const filteredCsvResults = csvResult?.predictions?.filter(e => {
    const matchesSearch = !csvSearch ||
      e.full_name?.toLowerCase().includes(csvSearch.toLowerCase()) ||
      e.employee_code?.toLowerCase().includes(csvSearch.toLowerCase()) ||
      e.department?.toLowerCase().includes(csvSearch.toLowerCase());
    const matchesLevel = csvFilterLevel === 'All' || e.threat_level === csvFilterLevel;
    return matchesSearch && matchesLevel;
  }) || [];

  // distributions
  const dist = pipelineResult ? {
    critical: pipelineResult.results?.filter(e => e.threat_level === 'Critical Risk').length || 0,
    high:     pipelineResult.results?.filter(e => e.threat_level === 'High Risk').length || 0,
    medium:   pipelineResult.results?.filter(e => e.threat_level === 'Medium Risk').length || 0,
    low:      pipelineResult.results?.filter(e => e.threat_level === 'Low Risk').length || 0,
  } : null;

  const manualMeta = manualResult ? (LEVEL_META[manualResult.threat_level] || LEVEL_META['Normal']) : null;
  const ManualIcon = manualMeta?.icon;

  return (
    <AppLayout title="Prediction Lab" subtitle="ML pipeline threat sweep + synthetic CSV upload & inference">
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>

        {/* ── Mode Tabs ── */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
          {[
            { id: 'pipeline', icon: ScanLine, label: 'ML Pipeline Scan', sub: 'Scan 300 synthetic cohort employees', color: '#f43f5e' },
            { id: 'csv',      icon: UploadCloud, label: 'CSV Upload Predict', sub: '50-row synthetic CSV predictions', color: '#00d4ff' },
            { id: 'manual',   icon: FlaskConical, label: 'Manual Vector Test', sub: 'Custom feature slider inference', color: '#a78bfa' },
          ].map(tab => {
            const TIcon = tab.icon;
            const active = mode === tab.id;
            return (
              <button key={tab.id} onClick={() => setMode(tab.id)} style={{
                flex: 1, display: 'flex', alignItems: 'center', gap: 12, padding: '14px 20px', borderRadius: 14, cursor: 'pointer',
                background: active ? `${tab.color}14` : 'rgba(255,255,255,0.03)',
                border: `1px solid ${active ? tab.color + '60' : 'rgba(255,255,255,0.08)'}`,
                transition: 'all 0.2s',
              }}>
                <div style={{ width: 40, height: 40, borderRadius: 11, background: active ? `${tab.color}25` : 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <TIcon size={18} color={active ? tab.color : 'var(--text-muted)'}/>
                </div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontWeight: 800, fontSize: '0.88rem', color: active ? tab.color : 'var(--text-secondary)' }}>{tab.label}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{tab.sub}</div>
                </div>
                {active && <div style={{ marginLeft: 'auto', width: 6, height: 6, borderRadius: '50%', background: tab.color, boxShadow: `0 0 8px ${tab.color}` }}/>}
              </button>
            );
          })}
        </div>

        {/* ════════════════ PIPELINE MODE ════════════════ */}
        {mode === 'pipeline' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 18 }}>
            <div>
              {/* Controls bar */}
              <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: '16px 20px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Sensitivity Filter</label>
                  <select value={minLevel} onChange={e => setMinLevel(e.target.value)} style={{ padding: '7px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)', fontSize: '0.78rem', cursor: 'pointer', outline: 'none' }}>
                    <option value="Normal">All Employees (Normal & above)</option>
                    <option value="Low Risk">All Risk Levels (Low–Critical)</option>
                    <option value="Medium Risk">Medium Risk &amp; above</option>
                    <option value="High Risk">High Risk &amp; above</option>
                    <option value="Critical Risk">Critical Risk only</option>
                  </select>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Feature Window</label>
                  <select value={scanDays} onChange={e => setScanDays(Number(e.target.value))} style={{ padding: '7px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)', fontSize: '0.78rem', cursor: 'pointer', outline: 'none' }}>
                    <option value={7}>Last 7 days</option>
                    <option value={14}>Last 14 days</option>
                    <option value={30}>Last 30 days</option>
                    <option value={60}>Last 60 days</option>
                  </select>
                </div>

                <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
                  <button onClick={handleReSeedSynthetic300} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 14px', borderRadius: 10, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 700, fontSize: '0.76rem', cursor: 'pointer' }}>
                    <RefreshCw size={13}/> Re-Seed 300 Cohort
                  </button>

                  <button onClick={runPipeline} disabled={pipelineLoading} style={{
                    display: 'flex', alignItems: 'center', gap: 8, padding: '9px 20px', borderRadius: 10,
                    background: pipelineLoading ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #f43f5e, #e11d48)',
                    border: 'none', color: '#fff', fontWeight: 800, fontSize: '0.8rem', cursor: pipelineLoading ? 'not-allowed' : 'pointer',
                    boxShadow: pipelineLoading ? 'none' : '0 4px 15px rgba(244,63,94,0.3)',
                  }}>
                    {pipelineLoading ? <RotateCcw size={14} style={{ animation: 'spin 1s linear infinite' }}/> : <ScanLine size={14}/>}
                    {pipelineLoading ? 'Scanning 300 Employees…' : 'Run Pipeline Scan'}
                  </button>
                </div>
              </div>

              {/* Progress bar */}
              {pipelineLoading && (
                <div style={{ background: 'var(--bg-card)', borderRadius: 12, border: '1px solid var(--border)', padding: '16px 20px', marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 6 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Running ML inference pipeline across synthetic employees…</span>
                    <strong style={{ color: '#f43f5e' }}>{progressPct}%</strong>
                  </div>
                  <div style={{ height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                    <div style={{ height: '100%', borderRadius: 3, background: 'linear-gradient(90deg,#f43f5e,#a78bfa)', width: `${progressPct}%`, transition: 'width 0.2s' }}/>
                  </div>
                </div>
              )}

              {/* Distribution summary */}
              {dist && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
                  {[
                    { label: 'Critical Risk', count: dist.critical, color: '#f43f5e', bg: 'rgba(244,63,94,0.1)' },
                    { label: 'High Risk',     count: dist.high,     color: '#f97316', bg: 'rgba(249,115,22,0.1)' },
                    { label: 'Medium Risk',   count: dist.medium,   color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
                    { label: 'Low Risk',      count: dist.low,      color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
                  ].map(c => (
                    <div key={c.label} style={{ padding: '12px 14px', borderRadius: 10, background: c.bg, border: `1px solid ${c.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ fontSize: '0.65rem', fontWeight: 700, color: c.color, letterSpacing: '0.06em' }}>{c.label}</div>
                        <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', lineHeight: 1, marginTop: 4 }}>{c.count}</div>
                      </div>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: c.color, boxShadow: `0 0 8px ${c.color}` }}/>
                    </div>
                  ))}
                </div>
              )}

              {/* Search & list */}
              {!pipelineResult && !pipelineLoading && (
                <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: '40px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <ScanLine size={40} style={{ margin: '0 auto 14px', opacity: 0.25 }}/>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 6 }}>No scan results yet</div>
                  <div style={{ fontSize: '0.75rem' }}>Click <strong style={{ color: '#f43f5e' }}>Run Pipeline Scan</strong> to run ML inference across the synthetic employee cohort.</div>
                </div>
              )}

              {pipelineResult && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                      <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}/>
                      <input type="text" placeholder="Search by name, employee code, or department..." value={searchQ} onChange={e => setSearchQ(e.target.value)}
                        style={{ width: '100%', padding: '8px 12px 8px 34px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-primary)', fontSize: '0.78rem', outline: 'none' }}
                      />
                    </div>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      Showing <strong>{filteredResults.length}</strong> of {pipelineResult.total_flagged} employees
                    </span>
                  </div>

                  {filteredResults.length === 0 ? (
                    <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 12, border: `1px solid ${pipelineResult.total_scanned === 0 ? 'rgba(244,63,94,0.25)' : 'rgba(255,255,255,0.07)'}`, padding: '32px 24px', textAlign: 'center' }}>
                      {pipelineResult.total_scanned === 0 ? (
                        <>
                          <Users size={32} style={{ margin: '0 auto 10px', opacity: 0.4 }} color="#f43f5e"/>
                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f43f5e', marginBottom: 6 }}>
                            Database has no active employees
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 14 }}>
                            The synthetic employee cohort has not been seeded yet. Click the button below to populate 300 synthetic employees.
                          </div>
                          <button onClick={handleReSeedSynthetic300} style={{
                            display: 'inline-flex', alignItems: 'center', gap: 6, padding: '9px 18px', borderRadius: 10,
                            background: 'linear-gradient(135deg,#f43f5e,#e11d48)', border: 'none',
                            color: '#fff', fontWeight: 800, fontSize: '0.78rem', cursor: 'pointer',
                            boxShadow: '0 4px 14px rgba(244,63,94,0.35)',
                          }}>
                            <RefreshCw size={13}/> Re-Seed 300 Cohort Now
                          </button>
                        </>
                      ) : (
                        <>
                          <CheckCircle size={32} style={{ margin: '0 auto 10px', opacity: 0.3 }} color="#10b981"/>
                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 4 }}>
                            {searchQ ? 'No employees match your search.' : `All ${pipelineResult.total_scanned} employees scored below the selected filter.`}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            {searchQ ? 'Try a different name or employee code.' : 'Switch the Sensitivity Filter to "All Employees" to see every prediction.'}
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div>
                      {filteredResults.map((emp, i) => (
                        <PipelineResultCard key={emp.employee_id || i} emp={emp} rank={i+1} onClick={setSelectedEmp} isSelected={selectedEmp?.employee_id === emp.employee_id}/>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* RIGHT — Detail drawer */}
            <div>
              {selectedEmp ? (
                <PipelineDetailPanel emp={selectedEmp} onClose={() => setSelectedEmp(null)}/>
              ) : (
                <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <Users size={32} style={{ margin: '0 auto 12px', opacity: 0.3 }}/>
                  <div>Select any employee from the pipeline scan results to inspect full AI predictions &amp; SHAP explanation.</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════════════ CSV MODE ════════════════ */}
        {mode === 'csv' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 18 }}>
            <div>
              {/* Upload Dropzone & Action Bar */}
              <div style={{ background: 'var(--bg-card)', borderRadius: 16, border: '1px solid var(--border)', padding: 20, marginBottom: 18 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                  <div>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                      <FileSpreadsheet color="#00d4ff" size={18}/> Synthetic CSV Batch Prediction
                    </h3>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      Upload a 50-row synthetic CSV file to run ML risk classification on custom criteria.
                    </div>
                  </div>
                  <button onClick={handleDownloadSampleCsv} style={{
                    display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 9,
                    background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)',
                    color: '#00d4ff', fontWeight: 700, fontSize: '0.75rem', cursor: 'pointer'
                  }}>
                    <Download size={13}/> Download Sample 50-Row CSV
                  </button>
                </div>

                {/* File Dropzone */}
                <div style={{
                  padding: '24px 20px', borderRadius: 12, border: '2px dashed rgba(0,212,255,0.3)',
                  background: csvFile ? 'rgba(0,212,255,0.06)' : 'rgba(255,255,255,0.02)',
                  textAlign: 'center', transition: 'all 0.2s', marginBottom: 14
                }}>
                  <input type="file" accept=".csv" id="synthetic-csv-input" onChange={e => setCsvFile(e.target.files[0])} style={{ display: 'none' }}/>
                  <label htmlFor="synthetic-csv-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                    <UploadCloud size={36} color={csvFile ? '#00d4ff' : 'var(--text-muted)'}/>
                    <div>
                      {csvFile ? (
                        <div style={{ fontWeight: 800, color: '#00d4ff', fontSize: '0.85rem' }}>📄 Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(1)} KB)</div>
                      ) : (
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', fontWeight: 700 }}>
                          Drag and drop your synthetic CSV file here, or <span style={{ color: '#00d4ff', textDecoration: 'underline' }}>Browse File</span>
                        </div>
                      )}
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 4 }}>Supports synthetic feature vectors (50+ rows containing Low, Medium, High, Critical criteria)</div>
                    </div>
                  </label>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                  {csvFile && (
                    <button onClick={() => { setCsvFile(null); setCsvResult(null); }} style={{ padding: '8px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)', fontSize: '0.75rem', cursor: 'pointer' }}>
                      Clear File
                    </button>
                  )}
                  <button onClick={handleCsvUpload} disabled={csvLoading || !csvFile} style={{
                    display: 'flex', alignItems: 'center', gap: 8, padding: '10px 22px', borderRadius: 10,
                    background: csvLoading || !csvFile ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #00d4ff, #0284c7)',
                    border: 'none', color: '#fff', fontWeight: 800, fontSize: '0.82rem', cursor: csvLoading || !csvFile ? 'not-allowed' : 'pointer',
                    boxShadow: csvLoading || !csvFile ? 'none' : '0 4px 15px rgba(0,212,255,0.3)'
                  }}>
                    {csvLoading ? <RotateCcw size={14} style={{ animation: 'spin 1s linear infinite' }}/> : <Zap size={14}/>}
                    {csvLoading ? 'Running ML Predictions…' : 'Upload & Predict CSV'}
                  </button>
                </div>
              </div>

              {/* CSV KPI Summary */}
              {csvResult && (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10, marginBottom: 16 }}>
                    <div style={{ padding: '12px 14px', borderRadius: 10, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Rows</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', marginTop: 4 }}>{csvResult.total_rows || 0}</div>
                    </div>
                    <div style={{ padding: '12px 14px', borderRadius: 10, background: 'rgba(244,63,94,0.1)', border: '1px solid #f43f5e30' }}>
                      <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#f43f5e', textTransform: 'uppercase' }}>Critical</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', marginTop: 4 }}>{csvResult.distribution?.['Critical Risk'] ?? 0}</div>
                    </div>
                    <div style={{ padding: '12px 14px', borderRadius: 10, background: 'rgba(249,115,22,0.1)', border: '1px solid #f9731630' }}>
                      <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#f97316', textTransform: 'uppercase' }}>High</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', marginTop: 4 }}>{csvResult.distribution?.['High Risk'] ?? 0}</div>
                    </div>
                    <div style={{ padding: '12px 14px', borderRadius: 10, background: 'rgba(245,158,11,0.1)', border: '1px solid #f59e0b30' }}>
                      <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase' }}>Medium</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', marginTop: 4 }}>{csvResult.distribution?.['Medium Risk'] ?? 0}</div>
                    </div>
                    <div style={{ padding: '12px 14px', borderRadius: 10, background: 'rgba(16,185,129,0.1)', border: '1px solid #10b98130' }}>
                      <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase' }}>Low</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#fff', marginTop: 4 }}>{csvResult.distribution?.['Low Risk'] ?? 0}</div>
                    </div>
                  </div>

                  {/* Filter & Search Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                      <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}/>
                      <input type="text" placeholder="Search CSV predictions by name, code, department..." value={csvSearch} onChange={e => setCsvSearch(e.target.value)}
                        style={{ width: '100%', padding: '8px 12px 8px 34px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-primary)', fontSize: '0.78rem', outline: 'none' }}
                      />
                    </div>
                    <select value={csvFilterLevel} onChange={e => setCsvFilterLevel(e.target.value)} style={{ padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)', fontSize: '0.78rem', cursor: 'pointer', outline: 'none' }}>
                      <option value="All">All Categories ({csvResult?.total_rows || 0})</option>
                      <option value="Critical Risk">Critical Risk ({csvResult?.distribution?.['Critical Risk'] ?? 0})</option>
                      <option value="High Risk">High Risk ({csvResult?.distribution?.['High Risk'] ?? 0})</option>
                      <option value="Medium Risk">Medium Risk ({csvResult?.distribution?.['Medium Risk'] ?? 0})</option>
                      <option value="Low Risk">Low Risk ({csvResult?.distribution?.['Low Risk'] ?? 0})</option>
                    </select>
                  </div>

                  {/* Prediction list */}
                  <div>
                    {filteredCsvResults.length > 0 ? (
                      filteredCsvResults.map((r, i) => (
                        <PipelineResultCard key={r.employee_code + i} emp={r} rank={r.row_index} onClick={setSelectedCsvRow} isSelected={selectedCsvRow?.employee_code === r.employee_code}/>
                      ))
                    ) : (
                      <div style={{ padding: 30, textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px dashed rgba(255,255,255,0.08)', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        <Info size={24} style={{ margin: '0 auto 8px', opacity: 0.5, color: '#00d4ff' }}/>
                        <div>No CSV prediction results match the current filter: <strong>{csvFilterLevel}</strong></div>
                        <button onClick={() => { setCsvFilterLevel('All'); setCsvSearch(''); }} style={{ marginTop: 10, padding: '6px 14px', borderRadius: 6, background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00d4ff', fontSize: '0.72rem', cursor: 'pointer', fontWeight: 700 }}>
                          Reset Filters (Show All {csvResult?.total_rows || 0} Rows)
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* RIGHT — Detail drawer for CSV row */}
            <div>
              {selectedCsvRow ? (
                <PipelineDetailPanel emp={selectedCsvRow} onClose={() => setSelectedCsvRow(null)}/>
              ) : (
                <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <FileSpreadsheet size={32} style={{ margin: '0 auto 12px', opacity: 0.3, color: '#00d4ff' }}/>
                  <div>Click any row from the uploaded CSV results to inspect full AI probabilities, top risk factors, and SHAP explanation.</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════════════ MANUAL MODE ════════════════ */}
        {mode === 'manual' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 18 }}>

            {/* LEFT — controls */}
            <div>
              {/* Presets bar */}
              <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: '14px 18px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Presets:</span>
                {Object.entries(PRESETS).map(([key, p]) => (
                  <button key={key} onClick={() => applyPreset(key)} style={{
                    padding: '5px 12px', borderRadius: 20, cursor: 'pointer',
                    background: activePreset === key ? `${p.color}25` : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${activePreset === key ? p.color : 'rgba(255,255,255,0.08)'}`,
                    color: activePreset === key ? p.color : 'var(--text-secondary)',
                    fontWeight: 700, fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 5,
                  }}>
                    <span>{p.icon}</span> {p.label}
                  </button>
                ))}
                <button onClick={() => { setFeatures(buildDefault()); setActivePreset(null); }} style={{ marginLeft: 'auto', padding: '5px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer' }}>
                  Reset All
                </button>
              </div>

              {/* Group tabs */}
              <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
                {FEATURE_GROUPS.map(g => {
                  const GIcon = g.icon;
                  const active = activeGroup === g.id;
                  return (
                    <button key={g.id} onClick={() => setActiveGroup(g.id)} style={{
                      padding: '8px 14px', borderRadius: 10, cursor: 'pointer',
                      background: active ? `${g.color}15` : 'rgba(255,255,255,0.03)',
                      border: `1px solid ${active ? g.color + '50' : 'rgba(255,255,255,0.07)'}`,
                      color: active ? g.color : 'var(--text-muted)',
                      fontWeight: 700, fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6,
                    }}>
                      <GIcon size={13}/>
                      {g.label}
                    </button>
                  );
                })}
              </div>

              {/* Slider form */}
              <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: 20 }}>
                {currentGroup && (
                  <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 800, color: currentGroup.color, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <currentGroup.icon size={15}/> {currentGroup.label} Features
                    </div>
                    {currentGroup.features.map(f => (
                      <FeatureSlider key={f.key} feature={f} value={features[f.key] ?? f.default} onChange={handleChange}/>
                    ))}
                  </div>
                )}

                <button onClick={runManual} disabled={manualLoading} style={{
                  width: '100%', marginTop: 10, padding: '12px', borderRadius: 10,
                  background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                  border: 'none', color: '#fff', fontWeight: 800, fontSize: '0.85rem', cursor: 'pointer',
                  boxShadow: '0 4px 15px rgba(139,92,246,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                }}>
                  {manualLoading ? <RotateCcw size={16} style={{ animation: 'spin 1s linear infinite' }}/> : <Zap size={16}/>}
                  {manualLoading ? 'Computing ML Inference…' : 'Run Inference on Features'}
                </button>
              </div>
            </div>

            {/* RIGHT — Manual Result output */}
            <div ref={resultRef}>
              {manualResult ? (
                <div style={{
                  background: 'var(--bg-card)', borderRadius: 16,
                  border: `1px solid ${manualMeta.color}40`, padding: 20,
                  boxShadow: `0 0 40px ${manualMeta.color}15`, animation: 'fadeInUp 0.3s ease-out',
                }}>
                  <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>Inference Output</div>

                  <div style={{
                    padding: '8px 12px', borderRadius: 8, marginBottom: 14,
                    background: manualResult.is_insider || manualResult.threat_score >= 50 ? 'rgba(244,63,94,0.15)' : 'rgba(16,185,129,0.15)',
                    border: `1px solid ${manualResult.is_insider || manualResult.threat_score >= 50 ? '#f43f5e' : '#10b981'}50`,
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 900, color: manualResult.is_insider || manualResult.threat_score >= 50 ? '#f43f5e' : '#10b981' }}>
                      {manualResult.is_insider || manualResult.threat_score >= 50 ? '🚨 INSIDER THREAT DETECTED' : '🛡️ BENIGN / NORMAL'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                    <ScoreRing score={manualResult.threat_score} size={90}/>
                    <div>
                      <LevelBadge level={manualResult.threat_level} size="lg"/>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 6 }}>
                        Confidence: <strong style={{ color: '#fff' }}>{manualResult.confidence?.toFixed(1)}%</strong>
                      </div>
                    </div>
                  </div>

                  {Object.entries(manualResult.class_probabilities || {}).map(([cls, prob]) => {
                    const cm = LEVEL_META[cls] || {}; const pct = Math.round((prob || 0) * 100); const isTop = cls === manualResult.threat_level;
                    return (
                      <div key={cls} style={{ marginBottom: 6 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', marginBottom: 2 }}>
                          <span style={{ color: isTop ? cm.color : 'var(--text-muted)', fontWeight: isTop ? 700 : 400 }}>{cls}</span>
                          <span style={{ color: cm.color || '#fff', fontWeight: 700 }}>{pct}%</span>
                        </div>
                        <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)' }}>
                          <div style={{ height: '100%', borderRadius: 2, background: cm.color || '#6366f1', width: `${pct}%`, transition: 'width 0.7s', boxShadow: isTop ? `0 0 6px ${cm.color}80` : 'none' }}/>
                        </div>
                      </div>
                    );
                  })}

                  {manualResult.top_features?.length > 0 && (
                    <div style={{ marginTop: 14 }}>
                      <div style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Top Risk Factors</div>
                      {manualResult.top_features.slice(0, 4).map((f, i) => (
                        <div key={f.feature} style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 5, padding: '5px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.03)' }}>
                          <span style={{ width: 16, height: 16, borderRadius: 4, background: `${manualMeta.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.58rem', fontWeight: 800, color: manualMeta.color }}>{i+1}</span>
                          <span style={{ flex: 1, fontSize: '0.68rem', color: 'var(--text-secondary)' }}>{f.feature.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-primary)' }}>{typeof f.contribution === 'number' ? `${(f.contribution * 100).toFixed(1)}%` : f.value}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {manualResult.recommended_action && (
                    <div style={{ marginTop: 12, padding: '8px 12px', borderRadius: 8, background: `${manualMeta.color}10`, border: `1px solid ${manualMeta.color}30` }}>
                      <div style={{ fontSize: '0.6rem', fontWeight: 700, color: manualMeta.color, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>⚡ Recommended Action</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-primary)', lineHeight: 1.55, fontWeight: 600 }}>{manualResult.recommended_action}</div>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ background: 'var(--bg-card)', borderRadius: 14, border: '1px solid var(--border)', padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <FlaskConical size={32} style={{ margin: '0 auto 12px', opacity: 0.3, color: '#a78bfa' }}/>
                  <div>Adjust feature sliders on the left and click "Run Inference" to generate custom risk predictions &amp; SHAP explanations.</div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes fadeInUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
      `}</style>
    </AppLayout>
  );
}
