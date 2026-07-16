import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { alerts as alertsApi } from '../lib/api';
import { useAuth, ROLES } from '../context/AuthContext';
import { Panel, SeverityPill, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './AlertQueue.css';

const SEVERITIES = ['', 'critical', 'high', 'medium', 'low', 'informational'];
const STATUSES = ['', 'new', 'acknowledged', 'investigating', 'escalated',
  'resolved_true_positive', 'resolved_false_positive'];

// The triage queue: a filterable table with row-level actions. This is where an
// analyst actually works - scan, filter, acknowledge, investigate, escalate.
export default function AlertQueue() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [severity, setSeverity] = useState('');
  const [status, setStatus] = useState('');
  const [openOnly, setOpenOnly] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const params = { limit: 100, open_only: openOnly };
  if (severity) params.severity = severity;
  if (status) params.status = status;

  const queue = useAsync(
    () => alertsApi.list(params),
    [severity, status, openOnly],
  );

  const act = useCallback(async (id, fn) => {
    setBusyId(id);
    try { await fn(id); await queue.reload(); }
    catch (e) { /* surfaced by row state; keep it quiet */ }
    finally { setBusyId(null); }
  }, [queue]);

  const rows = Array.isArray(queue.data) ? queue.data : [];

  return (
    <div className="queue">
      <motion.div className="queue__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Triage · work the queue</div>
          <h1 className="queue__title">Alert Queue</h1>
        </div>
      </motion.div>

      <Panel className="queue__panel" delay={0.05}
        eyebrow={`${rows.length} alert${rows.length === 1 ? '' : 's'} shown`}
        title="Open alerts"
        action={
          <div className="queue__filters">
            <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="qfilter">
              {SEVERITIES.map((s) => <option key={s} value={s}>{s || 'All severities'}</option>)}
            </select>
            <select value={status} onChange={(e) => setStatus(e.target.value)} className="qfilter">
              {STATUSES.map((s) => <option key={s} value={s}>{s ? s.replace(/_/g, ' ') : 'All statuses'}</option>)}
            </select>
            <label className="qtoggle">
              <input type="checkbox" checked={openOnly} onChange={(e) => setOpenOnly(e.target.checked)} />
              <span>Open only</span>
            </label>
          </div>
        }>
        {queue.loading ? <Loader label="Loading queue" />
          : queue.error ? <ErrorNote error={queue.error} onRetry={queue.reload} />
          : !rows.length ? <Empty label="No alerts match these filters." />
          : (
            <div className="qtable">
              <div className="qtable__head">
                <div>Severity</div>
                <div>Employee</div>
                <div className="qtable__num">Risk</div>
                <div className="qtable__num">Model</div>
                <div>Date</div>
                <div>Status</div>
                <div className="qtable__actions-h">Actions</div>
              </div>
              <div className="qtable__body">
                {rows.map((a, i) => (
                  <motion.div key={a.id} className="qrow"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    transition={{ delay: Math.min(i * 0.01, 0.3) }}>
                    <div><SeverityPill severity={a.severity} /></div>
                    <button className="qrow__uid mono" onClick={() => navigate(`/investigations/${a.user_id}`)}
                      title="Open case file">{a.user_id}</button>
                    <div className="qtable__num mono qrow__risk">{a.risk_score?.toFixed(0)}</div>
                    <div className="qtable__num mono qrow__prob">{(a.ml_probability * 100)?.toFixed(0)}%</div>
                    <div className="mono qrow__date">{a.alert_date}</div>
                    <div><StatusChip status={a.status} /></div>
                    <div className="qrow__actions">
                      {a.status === 'new' && (
                        <button className="qbtn" disabled={busyId === a.id}
                          onClick={() => act(a.id, alertsApi.acknowledge)}>Ack</button>
                      )}
                      {['new', 'acknowledged'].includes(a.status) && (
                        <button className="qbtn" disabled={busyId === a.id}
                          onClick={() => act(a.id, alertsApi.investigate)}>Investigate</button>
                      )}
                      {a.status !== 'escalated' && !a.status.startsWith('resolved') && (
                        <button className="qbtn qbtn--warn" disabled={busyId === a.id}
                          onClick={() => act(a.id, alertsApi.escalate)}>Escalate</button>
                      )}
                      {[ROLES.SECURITY_MANAGER, ROLES.ADMINISTRATOR].includes(user?.role)
                        && !a.status.startsWith('resolved') && (
                        <button className="qbtn qbtn--ok" disabled={busyId === a.id}
                          onClick={() => act(a.id, (id) => alertsApi.resolve(id, false))}>Resolve</button>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
      </Panel>
    </div>
  );
}

function StatusChip({ status }) {
  const label = status.replace(/_/g, ' ').replace('resolved ', '');
  const kind = status.startsWith('resolved') ? 'done'
    : status === 'escalated' ? 'esc'
    : status === 'investigating' ? 'inv'
    : status === 'acknowledged' ? 'ack' : 'new';
  return <span className={`statuschip statuschip--${kind}`}>{label}</span>;
}
