import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  LineChart, Line, Legend
} from 'recharts';
import {
  Users, AlertTriangle, Bell, Radar as RadarIcon,
  TrendingUp, Activity, Shield, Eye, ShieldAlert,
  Play, Pause, Volume2, VolumeX, Search, Clock,
  Monitor, Database, UploadCloud, KeyRound, Zap,
  Target, Network, BarChart2, ChevronUp, ChevronDown,
} from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner, ErrorState } from '../../components/common';
import { usePolling } from '../../hooks/useFetch';
import { dashboardAPI } from '../../api/client';
import { useLiveStore, triggerAudioAlert, triggerVoiceNotification } from '../../utils/store';
import axios from 'axios';

const RISK_COLOR = {
  critical: '#f43f5e',
  high:     '#f97316',
  medium:   '#f59e0b',
  low:      '#10b981',
  normal:   '#6366f1',
};

function getRiskColor(score) {
  if (score >= 75) return RISK_COLOR.critical;
  if (score >= 50) return RISK_COLOR.high;
  if (score >= 25) return RISK_COLOR.medium;
  if (score >= 12) return RISK_COLOR.low;
  return RISK_COLOR.normal;
}

function KPICard({ label, value, sub, color, icon: Icon, accentColor }) {
  return (
    <div className="stat-card" style={{ '--card-accent': accentColor || color }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 9,
          background: `${accentColor || color}18`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: `1px solid ${accentColor || color}30`,
        }}>
          <Icon size={15} color={accentColor || color} />
        </div>
        <div style={{
          fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.06em',
          textTransform: 'uppercase', color: accentColor || color,
          opacity: 0.8,
        }}>
          LIVE
        </div>
      </div>
      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', lineHeight: 1, marginBottom: 4 }}>
        {value ?? '—'}
      </div>
      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{sub}</div>
    </div>
  );
}

function MetricCard({ label, value, unit, description, color }) {
  return (
    <div style={{
      padding: '16px 18px',
      background: 'linear-gradient(135deg, rgba(10,15,30,0.9), rgba(5,8,18,0.95))',
      border: `1px solid ${color}22`,
      borderLeft: `3px solid ${color}`,
      borderRadius: 12,
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{ position: 'absolute', top: -10, right: -10, width: 60, height: 60, borderRadius: '50%', background: `${color}08` }} />
      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 4 }}>
        <span style={{ fontSize: '1.6rem', fontWeight: 800, color }}>{value}</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{unit}</span>
      </div>
      <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>{description}</div>
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [selectedPrediction, setSelectedPrediction] = useState(null);

  const liveActivities = useLiveStore(state => state.liveActivities);
  const employeeRiskScores = useLiveStore(state => state.employeeRiskScores);
  const demoModeActive = useLiveStore(state => state.demoModeActive);
  const setDemoMode = useLiveStore(state => state.setDemoMode);

  const token = localStorage.getItem('access_token');
  const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  const { data: baseStats, loading, error } = usePolling(
    () => dashboardAPI.analyst().then(r => r.data), [], 15000
  );
  const { data: baseSoc } = usePolling(
    () => dashboardAPI.soc().then(r => r.data), [], 15000
  );

  const riskList = Object.values(employeeRiskScores);
  const latestRiskUpdate = riskList.length > 0 ? riskList[riskList.length - 1] : null;

  useEffect(() => {
    if (latestRiskUpdate) setSelectedPrediction(latestRiskUpdate);
  }, [latestRiskUpdate]);

  const topEmployees = baseStats?.top_risk_employees || [];
  const mergedEmployees = [...topEmployees];

  riskList.forEach(liveScore => {
    const idx = mergedEmployees.findIndex(e => e.employee_id === liveScore.employee_code);
    const mapped = {
      employee_id: liveScore.employee_id,
      employee_name: liveScore.employee_name,
      employee_code: liveScore.employee_code,
      current_score: liveScore.total_score,
      risk_category: liveScore.risk_category,
      trend: liveScore.trend,
      open_alerts: liveScore.top_factors ? 1 : 0
    };
    if (idx >= 0) mergedEmployees[idx] = mapped;
    else mergedEmployees.push(mapped);
  });

  mergedEmployees.sort((a, b) => b.current_score - a.current_score);
  const filteredEmployees = mergedEmployees.filter(emp =>
    emp.employee_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employee_code?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleDemo = async () => {
    try {
      const nextMode = !demoModeActive;
      await axios.post(
        `${BASE_URL}/simulation/toggle`,
        { active: nextMode },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDemoMode(nextMode);
      if (soundEnabled) triggerAudioAlert('info');
      if (voiceEnabled) triggerVoiceNotification(`Simulation mode ${nextMode ? 'activated' : 'paused'}`);
    } catch (err) {
      console.error('Failed to toggle demo mode', err);
    }
  };

  if (loading && !baseStats) return <AppLayout title="SOC Dashboard"><Spinner /></AppLayout>;
  if (error) return <AppLayout title="SOC Dashboard"><ErrorState message={error} /></AppLayout>;

  const d = baseStats || {};
  const s = baseSoc || {};

  const riskDist = [
    { name: 'Critical', value: d.critical_risk_count || 3, color: RISK_COLOR.critical },
    { name: 'High',     value: d.high_risk_count || 7,    color: RISK_COLOR.high },
    { name: 'Medium',   value: d.medium_risk_count || 12, color: RISK_COLOR.medium },
    { name: 'Low',      value: d.low_risk_count || 18,    color: RISK_COLOR.low },
  ];

  const maxRiskScore = filteredEmployees.length > 0 ? filteredEmployees[0].current_score : 15;
  const needleAngle = (maxRiskScore / 100) * 180 - 90;

  const deptRadarData = [
    { subject: 'Engineering', Risk: 72, Baseline: 20 },
    { subject: 'Finance',     Risk: 41, Baseline: 35 },
    { subject: 'HR',          Risk: 58, Baseline: 15 },
    { subject: 'Sales',       Risk: 33, Baseline: 10 },
    { subject: 'Security',    Risk: 15, Baseline: 88 },
    { subject: 'Legal',       Risk: 28, Baseline: 30 },
  ];

  return (
    <AppLayout
      title="Security Operations Center"
      subtitle="Real-time behavioral threat intelligence & insider risk monitoring"
    >
      {/* ── Control Bar ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: 12, marginBottom: 20,
        padding: '12px 18px',
        background: 'rgba(0,0,0,0.3)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 7,
            padding: '6px 12px', borderRadius: 999,
            background: demoModeActive ? 'rgba(16,185,129,0.1)' : 'rgba(255,255,255,0.04)',
            border: `1px solid ${demoModeActive ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.08)'}`,
          }}>
            <div style={{
              width: 7, height: 7, borderRadius: '50%',
              background: demoModeActive ? '#10b981' : '#4a5878',
              boxShadow: demoModeActive ? '0 0 8px #10b981' : 'none',
              animation: demoModeActive ? 'pulse-ring 2s infinite' : 'none',
            }} />
            <span style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.08em', color: demoModeActive ? '#34d399' : 'var(--text-muted)' }}>
              SIMULATION: {demoModeActive ? 'RUNNING' : 'PAUSED'}
            </span>
          </div>

          <button onClick={handleToggleDemo} className="btn" style={{
            padding: '6px 14px', fontSize: '0.75rem',
            background: demoModeActive
              ? 'linear-gradient(135deg, #f43f5e, #be123c)'
              : 'linear-gradient(135deg, #10b981, #059669)',
            color: '#fff',
            boxShadow: demoModeActive ? '0 4px 15px rgba(244,63,94,0.3)' : '0 4px 15px rgba(16,185,129,0.3)',
          }}>
            {demoModeActive ? <Pause size={12} /> : <Play size={12} />}
            {demoModeActive ? 'Pause Feed' : 'Start Feed'}
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            style={{
              padding: '6px 10px', borderRadius: 8,
              background: soundEnabled ? 'rgba(0,212,255,0.1)' : 'rgba(255,255,255,0.04)',
              border: `1px solid ${soundEnabled ? 'rgba(0,212,255,0.25)' : 'rgba(255,255,255,0.06)'}`,
              color: soundEnabled ? 'var(--accent)' : 'var(--text-muted)',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5,
              fontSize: '0.72rem', fontWeight: 600,
            }}
            title="Toggle sound"
          >
            {soundEnabled ? <Volume2 size={12} /> : <VolumeX size={12} />}
            {soundEnabled ? 'Sound ON' : 'Sound OFF'}
          </button>

          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '6px 12px',
            background: 'rgba(0,0,0,0.3)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 8,
          }}>
            <Search size={12} color="var(--text-muted)" />
            <input
              className="form-input"
              style={{ border: 'none !important', padding: '0 !important', background: 'transparent !important', width: 160, fontSize: '0.78rem' }}
              placeholder="Search employees..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ── KPI Cards Row ── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: 14,
        marginBottom: 20,
      }}>
        <KPICard icon={Users}        label="Monitored Subjects"  value={d.total_employees_monitored ?? 42}  sub="Identity catalog"          accentColor="#00d4ff" />
        <KPICard icon={ShieldAlert}  label="Critical Risks"      value={d.critical_risk_count ?? 3}         sub="Immediate quarantine"      accentColor="#f43f5e" />
        <KPICard icon={Bell}         label="Open Alerts"         value={d.open_alerts_count ?? 18}          sub="Unreviewed events"         accentColor="#f97316" />
        <KPICard icon={AlertTriangle}label="Active Incidents"    value={d.open_incidents_count ?? 5}        sub="Investigation queue"       accentColor="#f59e0b" />
        <KPICard icon={RadarIcon}    label="Anomalies (24h)"     value={d.anomalies_today ?? 27}            sub="Behavioral deviations"     accentColor="#8b5cf6" />
        <KPICard icon={Activity}     label="DLP Events"          value={d.activity_volume_24h ?? 1240}      sub="Log ingested (24h)"        accentColor="#10b981" />
      </div>

      {/* ── MTTD / MTTI / MTTR Panel ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
        <MetricCard label="Mean Time To Detect"     value="4.2"  unit="min" description="Avg time from event to alert trigger"        color="#00d4ff" />
        <MetricCard label="Mean Time To Investigate" value="18"  unit="min" description="Avg time to open and triage an incident"     color="#8b5cf6" />
        <MetricCard label="Mean Time To Respond"    value="47"   unit="min" description="Avg time to containment or resolution"       color="#f59e0b" />
        <MetricCard label="Compliance Score"        value="94.3" unit="%"   description="SOC policy adherence and coverage score"     color="#10b981" />
      </div>

      {/* ── Main SOC Layout ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16, marginBottom: 18 }}>

        {/* Threat Gauge + Risk Distribution */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Network Severity Index
            </span>
            <ShieldAlert size={15} color={RISK_COLOR.critical} />
          </div>

          {/* SVG Gauge */}
          <div style={{ position: 'relative', width: 180, height: 100 }}>
            <svg width="180" height="95" viewBox="0 0 180 90">
              <path d="M 10 90 A 80 80 0 0 1 170 90" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="16" />
              <path d="M 10 90 A 80 80 0 0 1 70 28" fill="none" stroke={RISK_COLOR.low}      strokeWidth="16" strokeLinecap="round" />
              <path d="M 70 28 A 80 80 0 0 1 120 28" fill="none" stroke={RISK_COLOR.medium}  strokeWidth="16" strokeLinecap="round" />
              <path d="M 120 28 A 80 80 0 0 1 170 90" fill="none" stroke={RISK_COLOR.critical} strokeWidth="16" strokeLinecap="round" />
              <circle cx="90" cy="90" r="7" fill="#fff" />
            </svg>
            <div style={{
              position: 'absolute', bottom: -2, left: '50%',
              width: 3, height: 68,
              background: 'linear-gradient(to top, #fff, var(--accent))',
              borderRadius: 2,
              transformOrigin: 'bottom center',
              transform: `translateX(-50%) rotate(${needleAngle}deg)`,
              transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)',
            }} />
          </div>

          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Peak Fused Score</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: getRiskColor(maxRiskScore), lineHeight: 1.1 }}>
              {maxRiskScore?.toFixed(1)}
            </div>
          </div>

          {/* Risk breakdown dots */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 6, width: '100%', marginTop: 14,
            paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.05)',
          }}>
            {riskDist.map(r => (
              <div key={r.name} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: 2 }}>{r.name}</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: r.color, lineHeight: 1 }}>{r.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Anomaly Trend Chart */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Anomalous Signal Volume — 7-Day Matrix
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                <div style={{ width: 8, height: 2, borderRadius: 1, background: 'var(--accent)' }} />
                Anomalies
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                <div style={{ width: 8, height: 2, borderRadius: 1, background: RISK_COLOR.critical }} />
                Alerts
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={s.anomaly_trend_7d || [
              { date: 'Mon', anomaly_count: 14, alerts: 3 },
              { date: 'Tue', anomaly_count: 22, alerts: 5 },
              { date: 'Wed', anomaly_count: 18, alerts: 4 },
              { date: 'Thu', anomaly_count: 31, alerts: 8 },
              { date: 'Fri', anomaly_count: 27, alerts: 6 },
              { date: 'Sat', anomaly_count: 11, alerts: 2 },
              { date: 'Sun', anomaly_count: 19, alerts: 4 },
            ]}>
              <defs>
                <linearGradient id="areaGrad1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="var(--accent)"       stopOpacity={0.3} />
                  <stop offset="95%" stopColor="var(--accent)"       stopOpacity={0} />
                </linearGradient>
                <linearGradient id="areaGrad2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={RISK_COLOR.critical} stopOpacity={0.25} />
                  <stop offset="95%" stopColor={RISK_COLOR.critical} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} width={25} />
              <Tooltip contentStyle={{ background: '#0a0f1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 11 }} />
              <Area type="monotone" dataKey="anomaly_count" name="Anomalies" stroke="var(--accent)" fill="url(#areaGrad1)" strokeWidth={2} />
              <Area type="monotone" dataKey="alerts"        name="Alerts"   stroke={RISK_COLOR.critical} fill="url(#areaGrad2)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Live Feed + Risk Leaderboard ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 18 }}>

        {/* Live Log Feed */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, paddingBottom: 10, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981', animation: 'pulse-ring 2s infinite' }} />
              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                Real-Time Network Activity Feed
              </span>
            </div>
            <span style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>
              {liveActivities.length} events
            </span>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', maxHeight: 300, display: 'flex', flexDirection: 'column', gap: 5 }}>
            {liveActivities.map((act) => (
              <div key={act.id} style={{
                display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
                padding: '8px 10px',
                background: act.is_suspicious ? 'rgba(244,63,94,0.05)' : 'rgba(255,255,255,0.025)',
                border: `1px solid ${act.is_suspicious ? 'rgba(244,63,94,0.2)' : 'rgba(255,255,255,0.05)'}`,
                borderRadius: 8,
                transition: 'all 0.2s',
              }}>
                <div style={{ display: 'flex', gap: 8, flex: 1 }}>
                  <div style={{
                    padding: '3px 7px', borderRadius: 5,
                    background: 'rgba(0,212,255,0.08)',
                    border: '1px solid rgba(0,212,255,0.15)',
                    fontSize: '0.6rem', fontWeight: 700, color: 'var(--accent)',
                    fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap',
                    height: 'fit-content', marginTop: 1,
                  }}>
                    {act.activity_name}
                  </div>
                  <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {act.employee_name}
                      <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}> · {act.department}</span>
                    </div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>{act.description}</div>
                    <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>
                      {act.resource} · {act.source_ip}
                    </div>
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {new Date(act.timestamp).toLocaleTimeString()}
                  </div>
                  {act.is_suspicious && (
                    <div style={{
                      marginTop: 4, padding: '1px 6px', borderRadius: 4,
                      background: 'rgba(244,63,94,0.15)', color: '#f43f5e',
                      fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase',
                      border: '1px solid rgba(244,63,94,0.25)',
                    }}>
                      ANOMALY
                    </div>
                  )}
                </div>
              </div>
            ))}
            {liveActivities.length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                <Activity size={24} style={{ margin: '0 auto 10px', opacity: 0.3 }} />
                Awaiting live feed… Start simulation to see activity.
              </div>
            )}
          </div>
        </div>

        {/* Risk Leaderboard */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
              Risk Index Ranking
            </span>
            <button onClick={() => navigate('/risk')} style={{
              fontSize: '0.68rem', color: 'var(--accent)', fontWeight: 600,
              background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)',
              padding: '3px 8px', borderRadius: 6, cursor: 'pointer',
            }}>
              View All
            </button>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', maxHeight: 300, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {filteredEmployees.slice(0, 10).map((emp, index) => {
              const c = getRiskColor(emp.current_score);
              return (
                <div key={emp.employee_code} onClick={() => navigate(`/employees/${emp.employee_id}`)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 10px', borderRadius: 9,
                    background: 'rgba(255,255,255,0.025)',
                    border: '1px solid rgba(255,255,255,0.04)',
                    cursor: 'pointer', transition: 'all 0.15s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.025)'}
                >
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', width: 18, flexShrink: 0 }}>
                    #{index + 1}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.2 }} className="truncate">
                      {emp.employee_name}
                    </div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{emp.employee_code}</div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: c, lineHeight: 1 }}>
                      {emp.current_score?.toFixed(0)}
                    </div>
                    <div style={{ width: 40, height: 3, borderRadius: 2, background: 'rgba(255,255,255,0.06)', marginTop: 3 }}>
                      <div style={{ width: `${emp.current_score}%`, height: '100%', borderRadius: 2, background: c }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── AI Explainability Panel ── */}
      {selectedPrediction && (
        <div className="card" style={{
          marginBottom: 18,
          border: '1px solid rgba(0,212,255,0.12)',
          background: 'linear-gradient(135deg, rgba(0,212,255,0.02), rgba(10,15,30,0.95))',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, paddingBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 28, height: 28, borderRadius: 7, background: 'rgba(0,212,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <RadarIcon size={13} color="var(--accent)" />
              </div>
              <div>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  XAI Model Audit — {selectedPrediction.employee_name}
                </div>
                <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Explainable AI behavioral decomposition</div>
              </div>
            </div>
            <div style={{
              padding: '4px 10px', borderRadius: 6,
              background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)',
              fontSize: '0.7rem', color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontWeight: 700,
            }}>
              Confidence: {selectedPrediction.xgboost_probability?.toFixed(1) || '—'}%
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
            <div>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 12 }}>
                SHAP Feature Contributions
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {selectedPrediction.top_factors?.map((f, i) => {
                  const colors = ['#00d4ff', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e'];
                  const c = colors[i % colors.length];
                  const pct = Math.min(Math.max(f.score * 8, 5), 100);
                  return (
                    <div key={f.factor}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{f.factor}</span>
                        <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: c }}>{f.weight}</span>
                      </div>
                      <div style={{ height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: c, borderRadius: 3, transition: 'width 0.6s ease' }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div style={{ padding: 16, background: 'rgba(0,0,0,0.3)', borderRadius: 10, border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#f43f5e', textTransform: 'uppercase', marginBottom: 6 }}>AI Risk Interpretation</div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontStyle: 'italic' }}>
                "{selectedPrediction.shap_explanation}"
              </p>
              <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', marginBottom: 6 }}>Recommended Action</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-primary)', lineHeight: 1.5, fontWeight: 500 }}>
                  {selectedPrediction.recommended_action}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Bottom Visualizations ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

        {/* Department Radar */}
        <div className="card">
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            Department Threat Exposure — Peer Comparison
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={deptRadarData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 8 }} />
              <Radar name="Active Risk"  dataKey="Risk"     stroke={RISK_COLOR.critical} fill={RISK_COLOR.critical} fillOpacity={0.15} strokeWidth={2} />
              <Radar name="Security Baseline" dataKey="Baseline" stroke="var(--accent)"  fill="var(--accent)"  fillOpacity={0.1}  strokeWidth={2} />
              <Legend wrapperStyle={{ fontSize: 10, marginTop: 8 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Data Transfer Bars */}
        <div className="card">
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            Data Exfiltration Vector Analytics — Inbound / Outbound
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={[
              { name: 'Mon', downloads: 4000, uploads: 2400 },
              { name: 'Tue', downloads: 3000, uploads: 1800 },
              { name: 'Wed', downloads: 2200, uploads: 9800 },
              { name: 'Thu', downloads: 2780, uploads: 3908 },
              { name: 'Fri', downloads: 1890, uploads: 4800 },
              { name: 'Sat', downloads: 2390, uploads: 2100 },
              { name: 'Sun', downloads: 3490, uploads: 4300 },
            ]} barCategoryGap="35%">
              <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} width={30} />
              <Tooltip contentStyle={{ background: '#0a0f1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 11 }} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
              <Bar dataKey="downloads" name="File Downloads (MB)" fill="var(--accent)"       radius={[4,4,0,0]} />
              <Bar dataKey="uploads"   name="Cloud Uploads (MB)"  fill={RISK_COLOR.critical} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </AppLayout>
  );
}
