import React, { useState } from 'react';
import {
  Network, Users, TrendingUp, BarChart2, Activity,
  Shield, Target, AlertTriangle, Eye, Layers,
} from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  LineChart, Line, Legend, ScatterChart, Scatter, ZAxis,
} from 'recharts';

const DEPT_COLORS = {
  Engineering: '#00d4ff',
  Finance:     '#f59e0b',
  HR:          '#8b5cf6',
  Sales:       '#10b981',
  Security:    '#6366f1',
  Legal:       '#f43f5e',
};

const DEPARTMENTS = ['Engineering', 'Finance', 'HR', 'Sales', 'Security', 'Legal'];

// Mock UEBA Data
const peerGroupData = [
  { department: 'Engineering', avgRisk: 68, peerAvg: 22, deviation: 46, members: 12, anomalies: 8  },
  { department: 'Finance',     avgRisk: 41, peerAvg: 18, deviation: 23, members: 8,  anomalies: 3  },
  { department: 'HR',          avgRisk: 55, peerAvg: 20, deviation: 35, members: 6,  anomalies: 5  },
  { department: 'Sales',       avgRisk: 33, peerAvg: 15, deviation: 18, members: 14, anomalies: 2  },
  { department: 'Security',    avgRisk: 15, peerAvg: 85, deviation: -70,members: 5,  anomalies: 1  },
  { department: 'Legal',       avgRisk: 28, peerAvg: 12, deviation: 16, members: 4,  anomalies: 1  },
];

const behavioralTrend = [
  { week: 'W1', Engineering: 55, Finance: 30, HR: 45, Sales: 25, Security: 10 },
  { week: 'W2', Engineering: 60, Finance: 35, HR: 48, Sales: 28, Security: 12 },
  { week: 'W3', Engineering: 58, Finance: 38, HR: 52, Sales: 27, Security: 11 },
  { week: 'W4', Engineering: 65, Finance: 42, HR: 50, Sales: 30, Security: 13 },
  { week: 'W5', Engineering: 70, Finance: 40, HR: 55, Sales: 32, Security: 14 },
  { week: 'W6', Engineering: 68, Finance: 41, HR: 54, Sales: 33, Security: 15 },
];

const radarBehavior = [
  { metric: 'Login Anomaly',      Engineering: 80, Dept_avg: 25 },
  { metric: 'Data Transfer',      Engineering: 70, Dept_avg: 20 },
  { metric: 'After Hours',        Engineering: 60, Dept_avg: 15 },
  { metric: 'USB Usage',          Engineering: 45, Dept_avg: 10 },
  { metric: 'Privilege Abuse',    Engineering: 55, Dept_avg: 5  },
  { metric: 'VPN Anomaly',        Engineering: 65, Dept_avg: 18 },
  { metric: 'DB Access',          Engineering: 72, Dept_avg: 22 },
  { metric: 'Cloud Upload',       Engineering: 40, Dept_avg: 12 },
];

const topDeviators = [
  { name: 'Jane Smith',     dept: 'Engineering', deviation: 3.8, score: 82, status: 'Critical' },
  { name: 'Mike Johnson',   dept: 'HR',          deviation: 3.1, score: 68, status: 'High'     },
  { name: 'Alice Brown',    dept: 'Finance',      deviation: 2.7, score: 58, status: 'High'     },
  { name: 'Tom Davis',      dept: 'Engineering', deviation: 2.2, score: 51, status: 'Medium'   },
  { name: 'Sara Wilson',    dept: 'Sales',        deviation: 1.8, score: 42, status: 'Medium'   },
  { name: 'Robert Lee',     dept: 'Legal',        deviation: 1.4, score: 35, status: 'Low'      },
];

const STATUS_COLOR = { Critical: '#f43f5e', High: '#f97316', Medium: '#f59e0b', Low: '#10b981' };

export default function UEBAPage() {
  const [selectedDept, setSelectedDept] = useState('Engineering');

  return (
    <AppLayout
      title="UEBA Intelligence Engine"
      subtitle="User and Entity Behavioral Analytics — Peer group comparison, deviation scoring, and trend analysis"
    >
      {/* ── Overview KPIs ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 20 }}>
        {[
          { label: 'Entities Monitored', value: 49,    icon: Users,         color: '#00d4ff' },
          { label: 'Peer Groups',         value: 6,     icon: Network,       color: '#8b5cf6' },
          { label: 'Behavioral Outliers', value: 14,   icon: AlertTriangle, color: '#f43f5e' },
          { label: 'High Deviations',     value: 6,    icon: TrendingUp,    color: '#f97316' },
          { label: 'Avg Risk Score',       value: 40,   icon: Target,        color: '#f59e0b' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="stat-card" style={{ '--card-accent': color }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${color}28` }}>
                <Icon size={14} color={color} />
              </div>
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color, lineHeight: 1, marginBottom: 4 }}>{value}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* ── Department Selector ── */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {DEPARTMENTS.map(dept => {
          const c = DEPT_COLORS[dept];
          const active = selectedDept === dept;
          return (
            <button key={dept} onClick={() => setSelectedDept(dept)} style={{
              padding: '7px 16px', borderRadius: 999,
              background: active ? `${c}20` : 'rgba(255,255,255,0.03)',
              border: `1px solid ${active ? c : 'rgba(255,255,255,0.07)'}`,
              color: active ? c : 'var(--text-secondary)',
              fontSize: '0.78rem', fontWeight: active ? 700 : 500,
              cursor: 'pointer', transition: 'all 0.2s',
            }}>
              {dept}
            </button>
          );
        })}
      </div>

      {/* ── Main Charts Grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 18 }}>

        {/* Behavioral Radar — selected department vs avg */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            {selectedDept} — Behavioral Profile vs Peer Average
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarBehavior}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-muted)', fontSize: 9 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 7 }} />
              <Radar name={selectedDept}   dataKey="Engineering" stroke={DEPT_COLORS[selectedDept] || '#00d4ff'} fill={DEPT_COLORS[selectedDept] || '#00d4ff'} fillOpacity={0.18} strokeWidth={2} />
              <Radar name="Dept Average"    dataKey="Dept_avg"    stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} strokeWidth={1.5} strokeDasharray="4 2" />
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Department Risk Bar */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            Department Avg Risk vs Peer Security Baseline
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={peerGroupData} barCategoryGap="30%">
              <XAxis dataKey="department" tick={{ fill: 'var(--text-muted)', fontSize: 9 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 9 }} tickLine={false} axisLine={false} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: '#0a0f1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 11 }} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
              <Bar dataKey="avgRisk"  name="Dept Risk Score"   radius={[4,4,0,0]}>
                {peerGroupData.map((entry) => (
                  <Cell key={entry.department} fill={DEPT_COLORS[entry.department] || '#00d4ff'} />
                ))}
              </Bar>
              <Bar dataKey="peerAvg" name="Security Baseline" fill="#6366f1" fillOpacity={0.5} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Behavioral Trend Chart ── */}
      <div className="card" style={{ marginBottom: 18 }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
          Behavioral Risk Trend by Department — 6-Week History
        </div>
        <ResponsiveContainer width="100%" height={230}>
          <LineChart data={behavioralTrend}>
            <XAxis dataKey="week" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} domain={[0, 100]} width={30} />
            <Tooltip contentStyle={{ background: '#0a0f1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 11 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {Object.entries(DEPT_COLORS).map(([dept, color]) => (
              <Line key={dept} type="monotone" dataKey={dept} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Top Behavioral Deviators ── */}
      <div className="card" style={{ marginBottom: 18 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={14} color="#f43f5e" />
            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Top Behavioral Deviators — Statistical Outliers
            </span>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>σ = standard deviations from peer mean</div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Peer Deviation (σ)</th>
                <th>Risk Score</th>
                <th>Deviation Bar</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {topDeviators.map((emp, i) => {
                const sc = STATUS_COLOR[emp.status] || '#6366f1';
                const dc = DEPT_COLORS[emp.dept] || '#00d4ff';
                const pct = (emp.deviation / 4.0) * 100;
                return (
                  <tr key={emp.name}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>#{i + 1} {emp.name}</td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: dc, fontSize: '0.78rem', fontWeight: 600 }}>
                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: dc }} />
                        {emp.dept}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: sc, fontWeight: 700 }}>+{emp.deviation}σ</td>
                    <td>
                      <span style={{ color: sc, fontWeight: 800, fontSize: '0.9rem' }}>{emp.score}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>/100</span>
                    </td>
                    <td style={{ minWidth: 120 }}>
                      <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: sc, borderRadius: 3, transition: 'width 0.6s ease' }} />
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${emp.status.toLowerCase()}`}>{emp.status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Department Summary Cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {peerGroupData.map(dept => {
          const c = DEPT_COLORS[dept.department] || '#00d4ff';
          const deviationLabel = dept.deviation > 30 ? 'HIGH' : dept.deviation > 15 ? 'MEDIUM' : dept.deviation < 0 ? 'BELOW' : 'LOW';
          const deviationColor = dept.deviation > 30 ? '#f43f5e' : dept.deviation > 15 ? '#f59e0b' : dept.deviation < 0 ? '#10b981' : '#6366f1';
          return (
            <div key={dept.department} className="card" style={{ border: `1px solid ${c}20` }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 7, background: `${c}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${c}28` }}>
                    <Layers size={12} color={c} />
                  </div>
                  <span style={{ fontWeight: 700, color: c, fontSize: '0.82rem' }}>{dept.department}</span>
                </div>
                <span className="badge" style={{ background: `${deviationColor}15`, color: deviationColor, border: `1px solid ${deviationColor}30` }}>
                  {deviationLabel}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 10 }}>
                <div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginBottom: 2 }}>Avg Risk</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: c }}>{dept.avgRisk}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginBottom: 2 }}>Members</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>{dept.members}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginBottom: 2 }}>Anomalies</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f43f5e' }}>{dept.anomalies}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginBottom: 2 }}>Deviation</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: deviationColor }}>
                    {dept.deviation > 0 ? '+' : ''}{dept.deviation}
                  </div>
                </div>
              </div>
              <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
                <div style={{ width: `${dept.avgRisk}%`, height: '100%', background: c, borderRadius: 2 }} />
              </div>
            </div>
          );
        })}
      </div>
    </AppLayout>
  );
}
