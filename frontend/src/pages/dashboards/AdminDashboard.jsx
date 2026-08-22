import { useState } from 'react';
import { motion } from 'framer-motion';
import { audit, operators, data } from '../../lib/api';
import { ROLE_LABEL } from '../../context/AuthContext';
import { Panel, useAsync, ErrorNote, Empty } from '../../components/ui';
import Loader from '../../components/Loader';
import './AdminDashboard.css';

// Administrator: the back office. The audit log is the hero - this is the only
// role that can see it. Operator roster and platform stats alongside.
export default function AdminDashboard() {
  const [actionFilter, setActionFilter] = useState('');
  const stats = useAsync(() => data.stats(), []);
  const ops = useAsync(() => operators.list(), []);
  const actions = useAsync(() => audit.actions(), []);
  const log = useAsync(
    () => audit.list(actionFilter ? { limit: 40, action: actionFilter } : { limit: 40 }),
    [actionFilter],
  );

  return (
    <div className="adm">
      <motion.div className="adm__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Administration · platform control</div>
          <h1 className="adm__title">Control Room</h1>
        </div>
        <PlatformPulse stats={stats} ops={ops} />
      </motion.div>

      <div className="adm__grid">
        {/* the audit log - the hero */}
        <Panel className="adm__audit" eyebrow="Audit trail · every operator action"
          title="System activity log" delay={0.05}
          action={<ActionFilter actions={actions} value={actionFilter} onChange={setActionFilter} />}>
          <AuditStream state={log} />
        </Panel>

        {/* side column */}
        <div className="adm__side">
          <Panel eyebrow="Platform · ingested data" title="Dataset" delay={0.1}>
            <DatasetStats state={stats} />
          </Panel>

          <Panel eyebrow="Access · who runs this" title="Operators" delay={0.15}>
            <OperatorRoster state={ops} />
          </Panel>
        </div>
      </div>
    </div>
  );
}

function PlatformPulse({ stats, ops }) {
  const opCount = Array.isArray(ops.data) ? ops.data.length : null;
  return (
    <div className="pulse">
      <div className="pulse__item">
        <div className="pulse__n mono">{opCount != null ? opCount : '—'}</div>
        <div className="pulse__l">operators</div>
      </div>
      <div className="pulse__sep" />
      <div className="pulse__item">
        <div className="pulse__n mono">{stats.data ? fmt(stats.data.employees) : '—'}</div>
        <div className="pulse__l">monitored</div>
      </div>
      <div className="pulse__sep" />
      <div className="pulse__item">
        <div className="pulse__dot" />
        <div className="pulse__l">operational</div>
      </div>
    </div>
  );
}

function ActionFilter({ actions, value, onChange }) {
  const list = actions.data?.actions || [];
  return (
    <select className="actionfilter" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">All actions</option>
      {list.map((a) => (
        <option key={a.action} value={a.action}>{a.action} ({a.count})</option>
      ))}
    </select>
  );
}

function AuditStream({ state }) {
  if (state.loading) return <Loader label="Reading log" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const entries = state.data?.entries || [];
  if (!entries.length) return <Empty label="No matching audit entries." />;

  return (
    <div className="stream">
      <div className="stream__count mono">
        {fmt(state.data.total)} total events{state.data.total > entries.length ? ` · showing ${entries.length}` : ''}
      </div>
      <div className="stream__list">
        {entries.map((e, i) => (
          <motion.div key={e.id} className="stream__row"
            initial={{ opacity: 0, x: 6 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: Math.min(i * 0.015, 0.4), duration: 0.25 }}>
            <div className={`stream__action stream__action--${actionKind(e.action)}`}>{e.action}</div>
            <div className="stream__actor">
              <span className="stream__actor-name">{e.actor_name || e.actor_email || 'system'}</span>
              {e.actor_email && e.actor_name && <span className="stream__actor-email">{e.actor_email}</span>}
            </div>
            <div className="stream__ip mono">{e.ip_address || '—'}</div>
            <div className="stream__time mono">{fmtTime(e.timestamp)}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function DatasetStats({ state }) {
  if (state.loading) return <Loader label="Loading" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const d = state.data;
  const rows = [
    ['Employees', d.employees],
    ['Logon events', d.logon_events],
    ['Device events', d.device_events],
    ['File events', d.file_events],
    ['Email events', d.email_events],
    ['HTTP daily rows', d.http_daily_rows],
  ];
  return (
    <div className="dstats">
      {rows.map(([label, n]) => (
        <div key={label} className="dstats__row">
          <span className="dstats__label">{label}</span>
          <span className="dstats__val mono">{fmt(n)}</span>
        </div>
      ))}
    </div>
  );
}

function OperatorRoster({ state }) {
  if (state.loading) return <Loader label="Loading" />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  const ops = Array.isArray(state.data) ? state.data : [];
  if (!ops.length) return <Empty label="No operators." />;

  // Group by role for a quick org read.
  const byRole = {};
  ops.forEach((o) => { (byRole[o.role] = byRole[o.role] || []).push(o); });

  return (
    <div className="oproster">
      <div className="oproster__summary">
        {Object.entries(byRole).map(([role, list]) => (
          <div key={role} className="oproster__rolecount">
            <span className="oproster__rolecount-n mono">{list.length}</span>
            <span className="oproster__rolecount-l">{ROLE_LABEL[role] || role}</span>
          </div>
        ))}
      </div>
      <div className="oproster__list">
        {ops.slice(0, 8).map((o) => (
          <div key={o.id} className="oproster__row">
            <div className={`oproster__status ${o.is_active ? 'oproster__status--on' : 'oproster__status--off'}`} />
            <div className="oproster__email">{o.email}</div>
            <div className="oproster__role">{ROLE_LABEL[o.role] || o.role}</div>
          </div>
        ))}
        {ops.length > 8 && <div className="oproster__more mono">+{ops.length - 8} more</div>}
      </div>
    </div>
  );
}

// action.kind -> a colour band. auth = neutral, alert = signal, user = warn.
function actionKind(action = '') {
  if (action.startsWith('alert')) return 'alert';
  if (action.startsWith('user')) return 'user';
  if (action.includes('failed') || action.includes('blocked')) return 'fail';
  return 'auth';
}

function fmt(n) { return n == null ? '—' : n.toLocaleString('en-US'); }
function fmtTime(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false });
}
