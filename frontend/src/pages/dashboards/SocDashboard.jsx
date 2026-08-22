import { useMemo, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import '../../lib/charts';
import { gridColor, SEVERITY_COLORS } from '../../lib/charts';
import { dashboard, alerts as alertsApi } from '../../lib/api';
import { Panel, SeverityPill, SEV_ORDER, useAsync, ErrorNote, Empty } from '../../components/ui';
import Loader from '../../components/Loader';
import './SocDashboard.css';

// SOC Engineer: the live operations floor. The big activity chart is the "wall
// monitor"; everything below is rapid-scan signal. Denser than the analyst view.
export default function SocDashboard() {
  const [days, setDays] = useState(30);
  const trend = useAsync(() => dashboard.riskTrend(days), [days]);
  const breakdown = useAsync(() => dashboard.anomalyBreakdown(), []);
  const summary = useAsync(() => alertsApi.summary(), []);
  const recent = useAsync(() => alertsApi.list({ limit: 12, open_only: true }), []);

  return (
    <div className="soc">
      <motion.div className="soc__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">SOC operations · live floor</div>
          <h1 className="soc__title">Signal Monitor</h1>
        </div>
        <div className="soc__scanbar">
          {['14', '30', '90'].map((d) => (
            <button key={d} className={`soc__scanbtn ${days === +d ? 'soc__scanbtn--on' : ''}`}
              onClick={() => setDays(+d)}>{d}d</button>
          ))}
        </div>
      </motion.div>

      {/* HERO: the wall monitor */}
      <Panel className="soc__wall" eyebrow="Real-time alert stream · by severity"
        title="Activity across the estate" delay={0.05}>
        <WallChart state={trend} />
      </Panel>

      {/* the signal band */}
      <div className="soc__band">
        <Panel className="soc__sig" eyebrow="Anomaly signal" title="Component intensity" delay={0.1}>
          <ComponentDeepDive state={breakdown} />
        </Panel>

        <Panel className="soc__sig" eyebrow="Severity scan" title="Live severity mix" delay={0.15}>
          <SeverityScan summary={summary} />
        </Panel>

        <Panel className="soc__sig soc__feed" eyebrow="Newest first" title="Incoming alerts" delay={0.2}>
          <AlertFeed state={recent} />
        </Panel>
      </div>
    </div>
  );
}

function WallChart({ state }) {
  const chart = useMemo(() => {
    if (!state.data?.series) return null;
    const s = state.data.series;
    const order = ['critical', 'high', 'medium', 'low', 'informational'];
    return {
      labels: s.map((p) => p.date.slice(5)),
      datasets: order.map((sev) => ({
        label: sev,
        data: s.map((p) => p[sev] || 0),
        borderColor: SEVERITY_COLORS[sev],
        backgroundColor: hexA(SEVERITY_COLORS[sev], sev === 'critical' ? 0.3 : 0.14),
        fill: true, tension: 0.3, pointRadius: 0, pointHoverRadius: 3, borderWidth: 1.5,
      })),
    };
  }, [state.data]);
  if (state.loading) return <Loader label="Monitoring stream" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  if (!chart) return <Empty label="No signal in range." />;
  return <div className="soc__wallbox"><Line data={chart} options={wallOpts} /></div>;
}

const COMPONENT_LABEL = {
  behavioral_anomalies: 'Behavioural', privilege_misuse: 'Privilege',
  data_access_violations: 'Data access', access_pattern_deviations: 'Access pattern',
  historical_security_events: 'History',
};
function ComponentDeepDive({ state }) {
  if (state.loading) return <Loader label="Analysing" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const comps = state.data?.components || [];
  if (!comps.length) return <Empty label="No component data." />;
  return (
    <div className="deepdive">
      {comps.map((c, i) => (
        <div key={c.component} className="deepdive__row">
          <div className="deepdive__label">{COMPONENT_LABEL[c.component] || c.component}</div>
          <div className="deepdive__track">
            <motion.div className={`deepdive__fill ${i === 0 ? 'deepdive__fill--lead' : ''}`}
              initial={{ width: 0 }} animate={{ width: `${c.average}%` }}
              transition={{ duration: 0.6, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }} />
          </div>
          <div className="deepdive__val mono">{c.average.toFixed(0)}</div>
        </div>
      ))}
      <div className="deepdive__foot">avg across {fmt(state.data.alerts_considered)} alerts</div>
    </div>
  );
}

function SeverityScan({ summary }) {
  if (summary.loading) return <Loader label="Scanning" />;
  if (summary.error) return <ErrorNote error={summary.error} onRetry={summary.reload} />;
  const by = summary.data.by_severity || {};
  const total = Object.values(by).reduce((a, b) => a + b, 0) || 1;
  return (
    <div className="scan">
      {SEV_ORDER.map((sev) => {
        const n = by[sev] || 0;
        // Perceptual (sqrt) width so a dangerous 2% critical slice stays VISIBLE
        // next to a 70% informational one. The number shown is exact; only the
        // bar is scaled - making the small-but-serious severities readable is the
        // point of a scan.
        const maxN = Math.max(...Object.values(by), 1);
        const w = n > 0 ? Math.max(Math.sqrt(n / maxN) * 100, 4) : 0;
        return (
          <div key={sev} className="scan__row">
            <div className={`scan__chip scan__chip--${sev}`} />
            <div className="scan__name">{sev}</div>
            <div className="scan__bar"><div className={`scan__barfill scan__barfill--${sev}`}
              style={{ width: `${w}%` }} /></div>
            <div className="scan__n mono">{fmt(n)}</div>
          </div>
        );
      })}
    </div>
  );
}

function AlertFeed({ state }) {
  if (state.loading) return <Loader label="Loading feed" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const rows = Array.isArray(state.data) ? state.data : [];
  if (!rows.length) return <Empty label="Queue is clear." />;
  return (
    <div className="feed">
      {rows.map((a, i) => (
        <motion.div key={a.id} className="feed__row"
          initial={{ opacity: 0, x: 6 }} animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.02, duration: 0.25 }}>
          <SeverityPill severity={a.severity} />
          <span className="feed__uid mono">{a.user_id}</span>
          <span className="feed__score mono">{a.risk_score?.toFixed(0)}</span>
          <span className="feed__date mono">{a.alert_date?.slice(5)}</span>
        </motion.div>
      ))}
    </div>
  );
}

const wallOpts = {
  responsive: true, maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', align: 'end',
      labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true, padding: 14, color: '#9fb0c3', font: { size: 10 } } },
    tooltip: { backgroundColor: '#141b26', borderColor: '#2a3646', borderWidth: 1, padding: 10 },
  },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 20 } },
    y: { stacked: true, grid: { color: gridColor }, ticks: { precision: 0 }, beginAtZero: true },
  },
};

function fmt(n) { return n == null ? '—' : n.toLocaleString('en-US'); }
function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}
