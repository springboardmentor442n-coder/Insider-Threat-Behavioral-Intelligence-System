import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Shield, RefreshCw, Search, Calendar, ChevronRight, TrendingUp, TrendingDown, HelpCircle, CheckCircle, ShieldAlert } from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner, ErrorState, EmptyState, RiskBar, Modal, StatCard, SelectFilter, FilterRow } from '../../components/common';
import { useFetch } from '../../hooks/useFetch';
import { riskAPI } from '../../api/client';
import { riskBadge, fmtDT, scoreColor, apiError } from '../../utils/helpers';
import toast from 'react-hot-toast';

const RISK_COLOR = {
  critical: '#f43f5e',
  high:     '#f97316',
  medium:   '#f59e0b',
  low:      '#10b981',
  info:     '#6366f1',
};

const WEIGHTED_COMPONENTS = [
  { label: 'Behavioral Anomalies',      weight: 35, color: '#f43f5e', description: 'Login patterns, off-hours, device changes' },
  { label: 'Privilege Misuse Indicators',weight: 25, color: '#f97316', description: 'Escalation events, admin access, role violations' },
  { label: 'Data Access Violations',    weight: 20, color: '#f59e0b', description: 'File transfers, cloud uploads, USB exfiltration' },
  { label: 'Access Pattern Deviations', weight: 10, color: '#8b5cf6', description: 'VPN anomalies, geolocation changes, session duration' },
  { label: 'Historical Security Events',weight: 10, color: '#00d4ff', description: 'Past incidents, alerts history, investigation records' },
];

function WeightedScoringPanel() {
  return (
    <div className="card" style={{ marginBottom: 20, border: '1px solid rgba(0,212,255,0.1)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <div style={{ width: 28, height: 28, borderRadius: 7, background: 'rgba(0,212,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Shield size={13} color="var(--accent)" />
        </div>
        <div>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-primary)' }}>Insider Risk Score — Weighted Composition Model</div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Per documentation: Risk = Σ(Component × Weight)</div>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
        {WEIGHTED_COMPONENTS.map(({ label, weight, color, description }) => (
          <div key={label} style={{
            padding: '12px 14px', borderRadius: 10,
            background: `${color}08`, border: `1px solid ${color}22`,
            position: 'relative', overflow: 'hidden',
          }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: color, opacity: 0.7 }} />
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color, lineHeight: 1, marginBottom: 4 }}>{weight}%</div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, lineHeight: 1.3 }}>{label}</div>
            <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>{description}</div>
            <div style={{ marginTop: 8, height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
              <div style={{ width: `${weight * 2.86}%`, height: '100%', background: color, borderRadius: 2 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const TOOLTIP_STYLE = {
  background: 'rgba(7, 11, 23, 0.95)',
  border: '1px solid #1E2D4A',
  borderRadius: 10,
  fontSize: '11px',
  color: '#E8EDF5',
};

function RiskHistoryModal({ employeeId, open, onClose }) {
  const { data, loading } = useFetch(
    () => riskAPI.history(employeeId, { days: 30 }).then(r => r.data),
    [employeeId]
  );

  const chartData = (data || []).map(r => ({
    date: new Date(r.score_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    score: Math.round(r.total_score),
    category: r.risk_category,
  }));

  return (
    <Modal open={open} onClose={onClose} title={`Historical Risk Diagnostics: Subject #${employeeId}`} width={620}>
      {loading ? (
        <div className="py-24"><Spinner /></div>
      ) : (
        <div className="space-y-5">
          
          {/* Trend Chart */}
          <div className="bg-cyber-bg/50 border border-cyber-border/40 p-4 rounded-2xl">
            <h4 className="text-[10px] font-bold text-cyber-muted uppercase tracking-wider mb-4">
              30-Day Score Profile Movement
            </h4>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} width={25} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <ReferenceLine y={75} stroke={RISK_COLOR.critical} strokeDasharray="3 3" />
                <ReferenceLine y={50} stroke={RISK_COLOR.high}     strokeDasharray="3 3" />
                <ReferenceLine y={25} stroke={RISK_COLOR.medium}   strokeDasharray="3 3" />
                <Line type="monotone" dataKey="score" stroke="var(--accent)" strokeWidth={2.5}
                  dot={{ fill: 'var(--accent)', r: 3 }} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
            
            {/* Threshold Ranges */}
            <div className="flex gap-4 mt-3 flex-wrap">
              {[
                ['Critical', '≥75', RISK_COLOR.critical],
                ['High',     '≥50', RISK_COLOR.high],
                ['Medium',   '≥25', RISK_COLOR.medium],
                ['Low',      '<25', RISK_COLOR.low],
              ].map(([label, range, color]) => (
                <div key={label} className="flex items-center gap-1.5">
                  <div className="w-4 h-1.5 rounded" style={{ background: color }} />
                  <span className="text-[9px] text-cyber-dim uppercase font-bold">{label} {range}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tabular Score History */}
          <div className="space-y-2">
            <h4 className="text-[10px] font-bold text-cyber-muted uppercase tracking-wider">
              Recent Scoring Instances
            </h4>
            <div className="table-wrap max-h-48 overflow-y-auto pr-1 scrollbar-thin border border-cyber-border/40 rounded-xl">
              <table>
                <thead>
                  <tr>
                    <th>Score Date</th>
                    <th>Risk Index</th>
                    <th>Class</th>
                    <th>Trend Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[...(data || [])].reverse().slice(0, 10).map(r => (
                    <tr key={r.id}>
                      <td className="text-[10px] font-mono text-gray-400">{fmtDT(r.score_date)}</td>
                      <td><RiskBar score={r.total_score} /></td>
                      <td>{riskBadge(r.risk_category)}</td>
                      <td className="font-semibold text-[10px]"
                        style={{
                          color: r.trend === 'increasing' ? RISK_COLOR.critical
                               : r.trend === 'decreasing' ? RISK_COLOR.low
                               : 'var(--text-muted)',
                        }}
                      >
                        {r.trend === 'increasing' ? <TrendingUp size={11} className="inline mr-1" /> : r.trend === 'decreasing' ? <TrendingDown size={11} className="inline mr-1" /> : null}
                        {r.trend.toUpperCase()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </Modal>
  );
}

export default function RiskPage() {
  const [catFilter, setCatFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [scoring, setScoring] = useState(false);
  const [histEmp, setHistEmp] = useState(null);

  const { data, loading, error, refetch } = useFetch(
    () => riskAPI.leaderboard({ category: catFilter || undefined, limit: 100 }).then(r => r.data),
    [catFilter]
  );

  const scoreAll = async () => {
    setScoring(true);
    try { 
      await riskAPI.scoreAll(); 
      toast.success('Batch assessment queued successfully'); 
      refetch();
    } catch (err) { 
      toast.error(apiError(err)); 
    } finally { 
      setScoring(false); 
    }
  };

  const activeScores = data || [];
  const filteredLeaderboard = activeScores.filter(emp =>
    emp.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employee_id.toString().includes(searchQuery)
  );

  // Compute stats
  const stats = {
    critical: activeScores.filter(e => e.risk_category === 'critical').length,
    high:     activeScores.filter(e => e.risk_category === 'high').length,
    medium:   activeScores.filter(e => e.risk_category === 'medium').length,
    low:      activeScores.filter(e => e.risk_category === 'low').length,
  };

  return (
    <AppLayout title="Risk Scoring Console" subtitle="Composite insider threat scores with weighted risk model breakdown">
      
      {/* Weighted Risk Model Panel */}
      <WeightedScoringPanel />

      {/* Category Selection KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div
          onClick={() => setCatFilter(catFilter === 'critical' ? '' : 'critical')}
          className={`stat-card cursor-pointer border-l-4 hover:-translate-y-1 transition-all ${catFilter === 'critical' ? 'border-l-cyber-danger bg-cyber-danger/10 ring-1 ring-cyber-danger/40' : 'border-l-cyber-danger bg-cyber-card/40 border border-cyber-border'}`}
        >
          <span className="stat-label">Critical Risks</span>
          <span className="stat-value text-cyber-danger">{stats.critical}</span>
          <span className="stat-delta">Immediate Review</span>
        </div>

        <div
          onClick={() => setCatFilter(catFilter === 'high' ? '' : 'high')}
          className={`stat-card cursor-pointer border-l-4 hover:-translate-y-1 transition-all ${catFilter === 'high' ? 'border-l-cyber-warning bg-cyber-warning/10 ring-1 ring-cyber-warning/40' : 'border-l-cyber-warning bg-cyber-card/40 border border-cyber-border'}`}
        >
          <span className="stat-label">High Risks</span>
          <span className="stat-value text-cyber-warning">{stats.high}</span>
          <span className="stat-delta">Priority Action</span>
        </div>

        <div
          onClick={() => setCatFilter(catFilter === 'medium' ? '' : 'medium')}
          className={`stat-card cursor-pointer border-l-4 hover:-translate-y-1 transition-all ${catFilter === 'medium' ? 'border-l-yellow-400 bg-yellow-400/5 ring-1 ring-yellow-400/30' : 'border-l-yellow-400 bg-cyber-card/40 border border-cyber-border'}`}
        >
          <span className="stat-label">Medium Risks</span>
          <span className="stat-value text-yellow-400">{stats.medium}</span>
          <span className="stat-delta">Active Monitoring</span>
        </div>

        <div
          onClick={() => setCatFilter(catFilter === 'low' ? '' : 'low')}
          className={`stat-card cursor-pointer border-l-4 hover:-translate-y-1 transition-all ${catFilter === 'low' ? 'border-l-cyber-accent bg-cyber-accent/10 ring-1 ring-cyber-accent/30' : 'border-l-cyber-accent bg-cyber-card/40 border border-cyber-border'}`}
        >
          <span className="stat-label">Low Risks</span>
          <span className="stat-value text-cyber-accent">{stats.low}</span>
          <span className="stat-delta">Baseline Standard</span>
        </div>
      </div>

      {/* Filter and controls row */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between mb-4 bg-cyber-card/40 border border-cyber-border/80 px-4 py-3 rounded-2xl">
        <div className="flex flex-wrap gap-2 items-center w-full sm:w-auto">
          
          {/* Search bar */}
          <div className="relative w-full sm:w-48">
            <input
              type="text"
              placeholder="Search subjects..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full form-input pl-8 py-1.5 placeholder-gray-500"
            />
            <Search size={12} className="absolute left-3 top-3 text-gray-500" />
          </div>

          <SelectFilter
            value={catFilter}
            onChange={setCatFilter}
            options={['critical','high','medium','low'].map(v => ({ value: v, label: v.toUpperCase() + ' RISK' }))}
            placeholder="All Risk Ranks"
          />
        </div>

        <div className="flex gap-2 w-full sm:w-auto justify-end">
          <button
            className="btn btn-ghost text-[10px] px-3 font-bold flex items-center gap-1.5 hover:border-cyber-primary"
            onClick={scoreAll}
            disabled={scoring}
          >
            <RefreshCw size={11} className={scoring ? "animate-spin" : ""} />
            {scoring ? 'Assessing...' : 'Batch Score All'}
          </button>
          <button
            className="btn btn-ghost text-[10px] px-3 font-semibold"
            onClick={refetch}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Main Leaderboard Table */}
      <div className="card p-0 border border-cyber-border/80">
        {loading ? (
          <div className="py-24"><Spinner /></div>
        ) : error ? (
          <ErrorState message={error} />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Employee Name</th>
                  <th style={{ minWidth: 200 }}>Composite Score Index</th>
                  <th>Category</th>
                  <th>Trend</th>
                  <th>Flagged Anomalies (7d)</th>
                  <th>Triggered Alerts</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filteredLeaderboard.map((emp, idx) => (
                  <tr key={emp.employee_id} className="hover:bg-cyber-primary/5 transition-all">
                    <td>
                      <span className="mono text-[10px] font-bold text-cyber-dim">#{idx + 1}</span>
                    </td>
                    <td>
                      <div className="flex flex-col">
                        <span className="text-[11px] font-bold text-white leading-tight">{emp.employee_name}</span>
                        <span className="text-[9px] text-cyber-muted font-mono mt-0.5">{emp.employee_code || `EMP${emp.employee_id.toString().padStart(3, '0')}`}</span>
                      </div>
                    </td>
                    <td style={{ minWidth: 200 }} className="align-middle">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-black text-white w-8 font-mono">
                          {emp.current_score?.toFixed(1)}%
                        </span>
                        <div className="flex-1">
                          <RiskBar score={emp.current_score} />
                        </div>
                      </div>
                    </td>
                    <td>{riskBadge(emp.risk_category)}</td>
                    <td className="align-middle">
                      <span className="font-semibold text-[10px] flex items-center gap-1"
                        style={{
                          color: emp.trend === 'increasing' ? RISK_COLOR.critical
                               : emp.trend === 'decreasing' ? RISK_COLOR.low
                               : 'var(--text-muted)',
                        }}
                      >
                        {emp.trend === 'increasing' ? <TrendingUp size={11} /> : emp.trend === 'decreasing' ? <TrendingDown size={11} /> : null}
                        {emp.trend.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-[11px]"
                        style={{
                          color: emp.anomaly_count_7d > 0 ? RISK_COLOR.high : 'var(--text-muted)'
                        }}
                      >
                        {emp.anomaly_count_7d}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-[11px]"
                        style={{
                          color: emp.open_alerts > 0 ? RISK_COLOR.critical : 'var(--text-muted)'
                        }}
                      >
                        {emp.open_alerts}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost text-[10px] px-2.5 py-1 flex items-center gap-1 hover:border-cyber-primary"
                        onClick={() => setHistEmp(emp.employee_id)}
                      >
                        Risk History <ChevronRight size={10} />
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredLeaderboard.length === 0 && (
                  <tr>
                    <td colSpan={8}>
                      <EmptyState icon={Shield} message="No employee risk profiles compiled." />
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* History Popup */}
      {histEmp && (
        <RiskHistoryModal employeeId={histEmp} open={!!histEmp} onClose={() => setHistEmp(null)} />
      )}

    </AppLayout>
  );
}
