import { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import '../../lib/charts';
import { gridColor, SEVERITY_COLORS } from '../../lib/charts';
import { dashboard, alerts as alertsApi } from '../../lib/api';
import { Panel, useAsync, ErrorNote, Empty } from '../../components/ui';
import Loader from '../../components/Loader';
import './ManagerDashboard.css';

// Security Manager: the briefing. Posture up top as big numbers, trend as the
// centrepiece, an accountability roster below. Editorial - fewer, larger elements.
export default function ManagerDashboard() {
  const summary = useAsync(() => alertsApi.summary(), []);
  const trend = useAsync(() => dashboard.riskTrend(90), []);
  const topRisks = useAsync(() => dashboard.topRisks(10), []);

  return (
    <div className="mgr">
      <motion.div className="mgr__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Command view · organisational posture</div>
          <h1 className="mgr__title">Risk Briefing</h1>
        </div>
        <div className="mgr__period mono">LAST 90 DAYS</div>
      </motion.div>

      {/* posture - the executive numbers */}
      <Posture summary={summary} />

      {/* trend as the centrepiece */}
      <Panel className="mgr__trend" eyebrow="Alert trajectory · 90 days"
        title="Is the organisation getting safer?" delay={0.1}>
        <TrendBig state={trend} />
      </Panel>

      {/* accountability roster */}
      <Panel className="mgr__roster" eyebrow="Ranked by peak risk · watch these people"
        title="Accountability roster" delay={0.15}>
        <Roster state={topRisks} />
      </Panel>
    </div>
  );
}

function Posture({ summary }) {
  if (summary.loading) return <div className="mgr__posture"><Loader label="Assessing posture" /></div>;
  if (summary.error) return <ErrorNote error={summary.error} onRetry={summary.reload} />;
  const d = summary.data;
  const by = d.by_severity || {};
  const crit = by.critical || 0;
  const high = by.high || 0;
  const actionable = crit + high;
  const total = d.total || 1;
  const actionablePct = ((actionable / total) * 100).toFixed(1);

  return (
    <motion.div className="mgr__posture"
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.05 }}>
      <div className="posture__main">
        <div className="posture__main-label eyebrow">Actionable exposure</div>
        <div className="posture__main-val mono">{fmt(actionable)}</div>
        <div className="posture__main-sub">
          critical + high alerts · <span className="mono">{actionablePct}%</span> of all activity
        </div>
      </div>
      <div className="posture__stats">
        <PostureStat label="Critical" value={fmt(crit)} tone="critical" />
        <PostureStat label="High" value={fmt(high)} tone="high" />
        <PostureStat label="Open" value={fmt(d.open)} tone="signal" />
        <PostureStat label="Unassigned" value={fmt(d.unassigned_open)} tone="mid" />
      </div>
    </motion.div>
  );
}

function PostureStat({ label, value, tone }) {
  return (
    <div className={`pstat pstat--${tone}`}>
      <div className="pstat__val mono">{value}</div>
      <div className="pstat__label">{label}</div>
    </div>
  );
}

function TrendBig({ state }) {
  const chart = useMemo(() => {
    if (!state.data?.series) return null;
    const s = state.data.series;
    // Manager view emphasises the serious end - only critical + high, as filled
    // areas. The noise (informational) is not the executive's concern.
    return {
      labels: s.map((p) => p.date.slice(5)),
      datasets: [
        {
          label: 'Critical', data: s.map((p) => p.critical || 0),
          borderColor: SEVERITY_COLORS.critical,
          backgroundColor: hexA(SEVERITY_COLORS.critical, 0.25),
          fill: true, tension: 0.35, pointRadius: 0, borderWidth: 2,
        },
        {
          label: 'High', data: s.map((p) => p.high || 0),
          borderColor: SEVERITY_COLORS.high,
          backgroundColor: hexA(SEVERITY_COLORS.high, 0.15),
          fill: true, tension: 0.35, pointRadius: 0, borderWidth: 2,
        },
      ],
    };
  }, [state.data]);
  if (state.loading) return <Loader label="Plotting trajectory" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  if (!chart) return <Empty label="No trend data." />;
  return <div className="mgr__trendbox"><Line data={chart} options={trendOpts} /></div>;
}

function Roster({ state }) {
  if (state.loading) return <Loader label="Ranking" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const emps = state.data?.employees || [];
  if (!emps.length) return <Empty label="No employees flagged." />;
  const max = Math.max(...emps.map((e) => e.peak_risk_score), 1);

  return (
    <div className="roster">
      {emps.map((e, i) => (
        <motion.div key={e.user_id} className="roster__row"
          initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04, duration: 0.3 }}>
          <div className="roster__rank mono">{String(i + 1).padStart(2, '0')}</div>
          <div className="roster__who">
            <div className="roster__name mono">{e.user_id}</div>
            <div className="roster__meta">
              {e.employee_name && <span>{e.employee_name}</span>}
              {e.department && <span className="roster__dept">· {e.department}</span>}
            </div>
          </div>
          <div className="roster__activity">
            <div className="roster__act-n mono">{e.alert_count}</div>
            <div className="roster__act-l">alerts</div>
          </div>
          <div className="roster__risk">
            <div className="roster__risk-track">
              <motion.div className="roster__risk-fill"
                initial={{ width: 0 }} animate={{ width: `${(e.peak_risk_score / max) * 100}%` }}
                transition={{ duration: 0.6, delay: i * 0.04 }} />
            </div>
            <div className="roster__risk-val mono">{e.peak_risk_score.toFixed(0)}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

const trendOpts = {
  responsive: true, maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'top', align: 'end',
      labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true, padding: 16, color: '#9fb0c3', font: { size: 11 } } },
    tooltip: { backgroundColor: '#141b26', borderColor: '#2a3646', borderWidth: 1, padding: 12 },
  },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 24 } },
    y: { grid: { color: gridColor }, ticks: { precision: 0 }, beginAtZero: true },
  },
};

function fmt(n) { return n == null ? '—' : n.toLocaleString('en-US'); }
function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}
