import { useMemo, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import '../../lib/charts';
import { gridColor, SEVERITY_COLORS } from '../../lib/charts';
import { dashboard, alerts as alertsApi } from '../../lib/api';
import {
  Panel, Metric, SeverityPill, SEV_ORDER, useAsync, ErrorNote, Empty,
} from '../../components/ui';
import Loader from '../../components/Loader';
import './AnalystDashboard.css';

export default function AnalystDashboard() {
  const [trendDays, setTrendDays] = useState(30);

  const summary = useAsync(() => alertsApi.summary(), []);
  const trend = useAsync(() => dashboard.riskTrend(trendDays), [trendDays]);
  const breakdown = useAsync(() => dashboard.anomalyBreakdown(), []);
  const topRisks = useAsync(() => dashboard.topRisks(8), []);

  return (
    <div className="analyst">
      <PageHeader />

      {/* --- headline metrics row --- */}
      <div className="analyst__metrics">
        <MetricsStrip summary={summary} />
      </div>

      {/* --- main grid --- */}
      <div className="analyst__grid">
        <Panel
          className="analyst__trend"
          eyebrow="Alert volume · by severity"
          title="Threat activity over time"
          delay={0.05}
          action={<RangeToggle value={trendDays} onChange={setTrendDays} />}
        >
          <TrendChart state={trend} />
        </Panel>

        <Panel
          className="analyst__breakdown"
          eyebrow="Risk components"
          title="What is driving alerts"
          delay={0.1}
        >
          <BreakdownChart state={breakdown} />
        </Panel>

        <Panel
          className="analyst__queue"
          eyebrow="Triage · by severity"
          title="Queue composition"
          delay={0.15}
        >
          <QueueBreakdown summary={summary} />
        </Panel>

        <Panel
          className="analyst__watch"
          eyebrow="Ranked by peak risk"
          title="Employees to watch"
          delay={0.2}
        >
          <WatchList state={topRisks} />
        </Panel>
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <motion.div
      className="analyst__header"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div>
        <div className="eyebrow">Analyst workspace</div>
        <h1 className="analyst__title">Threat Overview</h1>
      </div>
      <div className="analyst__ts mono">
        <span className="analyst__ts-dot" />
        LIVE · updated just now
      </div>
    </motion.div>
  );
}

// --- headline metrics ------------------------------------------------------
function MetricsStrip({ summary }) {
  if (summary.loading) return <div className="analyst__metrics-load"><Loader label="Loading queue" /></div>;
  if (summary.error) return <ErrorNote error={summary.error} onRetry={summary.reload} />;
  const d = summary.data;
  const crit = d.by_severity?.critical || 0;
  const high = d.by_severity?.high || 0;

  return (
    <>
      <Metric label="Open alerts" value={fmt(d.open)} tone="signal"
        sub={`${fmt(d.total)} total in system`} />
      <Metric label="Critical" value={fmt(crit)} tone="critical"
        sub="highest severity" />
      <Metric label="High" value={fmt(high)} tone="warn"
        sub="act soon" />
      <Metric label="Unassigned" value={fmt(d.unassigned_open)} tone="default"
        sub="awaiting an analyst" />
    </>
  );
}

// --- trend line chart ------------------------------------------------------
function TrendChart({ state }) {
  const chart = useMemo(() => {
    if (!state.data?.series) return null;
    const s = state.data.series;
    const labels = s.map((p) => p.date.slice(5)); // MM-DD
    // Stacked area, calm-to-hot bottom-to-top, so the eye sees the red band grow.
    const order = ['critical', 'high', 'medium', 'low', 'informational'];
    const datasets = order.map((sev) => ({
      label: sev,
      data: s.map((p) => p[sev] || 0),
      borderColor: SEVERITY_COLORS[sev],
      backgroundColor: hexA(SEVERITY_COLORS[sev], sev === 'critical' ? 0.28 : 0.16),
      fill: true,
      tension: 0.35,
      pointRadius: 0,
      pointHoverRadius: 3,
      borderWidth: 1.5,
    }));
    return { labels, datasets };
  }, [state.data]);

  if (state.loading) return <Loader label="Charting activity" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  if (!chart || !state.data.series.length) return <Empty label="No alerts in this range." />;

  const total = state.data.total_alerts;
  return (
    <div className="chart-wrap">
      <div className="chart-wrap__meta">
        <span className="mono">{fmt(total)}</span> alerts across{' '}
        <span className="mono">{state.data.days}</span> days
      </div>
      <div className="chart-box chart-box--tall">
        <Line data={chart} options={lineOpts} />
      </div>
    </div>
  );
}

// --- component breakdown (horizontal bar) ----------------------------------
const COMPONENT_LABEL = {
  behavioral_anomalies: 'Behavioural',
  privilege_misuse: 'Privilege',
  data_access_violations: 'Data access',
  access_pattern_deviations: 'Access pattern',
  historical_security_events: 'History',
};
function BreakdownChart({ state }) {
  const chart = useMemo(() => {
    if (!state.data?.components) return null;
    const c = state.data.components;
    return {
      labels: c.map((x) => COMPONENT_LABEL[x.component] || x.component),
      datasets: [{
        data: c.map((x) => x.average),
        backgroundColor: c.map((_, i) =>
          i === 0 ? '#22d3ee' : hexA('#22d3ee', 0.35 - i * 0.04)),
        borderRadius: 4,
        barThickness: 18,
      }],
    };
  }, [state.data]);

  if (state.loading) return <Loader label="Reading components" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  if (!chart) return <Empty label="No component data." />;

  return (
    <div className="chart-wrap">
      <div className="chart-wrap__meta">
        avg score across <span className="mono">{fmt(state.data.alerts_considered)}</span> alerts
      </div>
      <div className="chart-box">
        <Bar data={chart} options={barOpts} />
      </div>
    </div>
  );
}

// --- queue composition (severity pills + proportion bar) -------------------
function QueueBreakdown({ summary }) {
  if (summary.loading) return <Loader label="Loading" />;
  if (summary.error) return <ErrorNote error={summary.error} onRetry={summary.reload} />;
  const by = summary.data.by_severity || {};
  const total = Object.values(by).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="queuebreak">
      <div className="queuebreak__bar">
        {SEV_ORDER.map((sev) => {
          const n = by[sev] || 0;
          if (!n) return null;
          return (
            <div
              key={sev}
              className={`queuebreak__seg queuebreak__seg--${sev}`}
              style={{ width: `${(n / total) * 100}%` }}
              title={`${sev}: ${n}`}
            />
          );
        })}
      </div>
      <div className="queuebreak__list">
        {SEV_ORDER.map((sev) => (
          <div key={sev} className="queuebreak__row">
            <SeverityPill severity={sev} count={by[sev] || 0} />
            <span className="queuebreak__pct mono">
              {(((by[sev] || 0) / total) * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// --- watch list ------------------------------------------------------------
function WatchList({ state }) {
  if (state.loading) return <Loader label="Ranking" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const emps = state.data?.employees || [];
  if (!emps.length) return <Empty label="No employees flagged." />;

  const maxScore = Math.max(...emps.map((e) => e.peak_risk_score), 1);

  return (
    <div className="watch">
      {emps.map((e, i) => (
        <motion.div
          key={e.user_id}
          className="watch__row"
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.03 * i, duration: 0.3 }}
        >
          <div className="watch__rank mono">{String(i + 1).padStart(2, '0')}</div>
          <div className="watch__id">
            <div className="watch__uid mono">{e.user_id}</div>
            <div className="watch__dept">{e.department || '—'}</div>
          </div>
          <div className="watch__meter">
            <div className="watch__meter-track">
              <div
                className="watch__meter-fill"
                style={{ width: `${(e.peak_risk_score / maxScore) * 100}%` }}
              />
            </div>
            <div className="watch__score mono">{e.peak_risk_score.toFixed(0)}</div>
          </div>
          <div className="watch__count" title="total alerts for this employee">
            <span className="mono">{e.alert_count}</span>
            <span className="watch__count-cap">alerts</span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

function RangeToggle({ value, onChange }) {
  return (
    <div className="rangetoggle">
      {[14, 30, 90].map((d) => (
        <button
          key={d}
          className={`rangetoggle__btn ${value === d ? 'rangetoggle__btn--on' : ''}`}
          onClick={() => onChange(d)}
        >
          {d}d
        </button>
      ))}
    </div>
  );
}

// --- chart option objects --------------------------------------------------
const lineOpts = {
  responsive: true, maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom', align: 'end',
      labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true, padding: 14,
        color: '#9fb0c3', font: { size: 10 } },
    },
    tooltip: {
      backgroundColor: '#141b26', borderColor: '#2a3646', borderWidth: 1,
      padding: 10, titleColor: '#e7edf5', bodyColor: '#9fb0c3',
      titleFont: { family: "'JetBrains Mono'", size: 11 },
    },
  },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 16 } },
    y: { stacked: true, grid: { color: gridColor }, ticks: { precision: 0 }, beginAtZero: true },
  },
};

const barOpts = {
  indexAxis: 'y', responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#141b26', borderColor: '#2a3646', borderWidth: 1, padding: 10,
      callbacks: { label: (c) => ` avg ${c.parsed.x.toFixed(1)}` },
    },
  },
  scales: {
    x: { grid: { color: gridColor }, beginAtZero: true, max: 100 },
    y: { grid: { display: false } },
  },
};

// --- helpers ---------------------------------------------------------------
function fmt(n) {
  if (n == null) return '—';
  return n.toLocaleString('en-US');
}
function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}
