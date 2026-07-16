import { useState } from 'react';
import { motion } from 'framer-motion';
import { audit } from '../lib/api';
import { Panel, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './AuditLog.css';

// The full audit trail as its own page (admin-only, guarded in the router too).
// Same data as the admin dashboard's hero panel, but paginated deeper.
export default function AuditLog() {
  const [action, setAction] = useState('');
  const [offset, setOffset] = useState(0);
  const PAGE = 60;
  const actions = useAsync(() => audit.actions(), []);
  const log = useAsync(
    () => audit.list({ limit: PAGE, offset, ...(action ? { action } : {}) }),
    [action, offset],
  );

  const entries = log.data?.entries || [];
  const total = log.data?.total || 0;

  return (
    <div className="alog">
      <motion.div className="alog__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Administrator · full trail</div>
          <h1 className="alog__title">Audit Log</h1>
        </div>
      </motion.div>

      <Panel delay={0.05}
        eyebrow={`${fmt(total)} total events`}
        title="Every operator action"
        action={
          <select value={action} onChange={(e) => { setAction(e.target.value); setOffset(0); }} className="alog__filter">
            <option value="">All actions</option>
            {(actions.data?.actions || []).map((a) => (
              <option key={a.action} value={a.action}>{a.action} ({a.count})</option>
            ))}
          </select>
        }>
        {log.loading ? <Loader label="Reading trail" />
          : log.error ? <ErrorNote error={log.error} onRetry={log.reload} />
          : !entries.length ? <Empty label="No matching entries." />
          : (
            <>
              <div className="alogtable">
                <div className="alogtable__head">
                  <div>Action</div><div>Operator</div><div>Detail</div><div>IP</div><div>When</div>
                </div>
                <div className="alogtable__body">
                  {entries.map((e, i) => (
                    <motion.div key={e.id} className="alogrow"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      transition={{ delay: Math.min(i * 0.008, 0.3) }}>
                      <div className={`alogrow__action alogrow__action--${actionKind(e.action)}`}>{e.action}</div>
                      <div className="alogrow__actor">
                        <span className="alogrow__actor-name">{e.actor_name || e.actor_email || 'system'}</span>
                        {e.actor_email && <span className="alogrow__actor-email">{e.actor_email}</span>}
                      </div>
                      <div className="alogrow__detail">{e.detail || '—'}</div>
                      <div className="alogrow__ip mono">{e.ip_address || '—'}</div>
                      <div className="alogrow__time mono">{fmtTime(e.timestamp)}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
              <div className="alog__pager">
                <button className="qbtn" disabled={offset === 0}
                  onClick={() => setOffset(Math.max(0, offset - PAGE))}>← Newer</button>
                <span className="alog__pageinfo mono">
                  {offset + 1}–{Math.min(offset + PAGE, total)} of {fmt(total)}
                </span>
                <button className="qbtn" disabled={offset + PAGE >= total}
                  onClick={() => setOffset(offset + PAGE)}>Older →</button>
              </div>
            </>
          )}
      </Panel>
    </div>
  );
}

function actionKind(action = '') {
  if (action.startsWith('alert')) return 'alert';
  if (action.startsWith('user')) return 'user';
  if (action.includes('failed') || action.includes('blocked')) return 'fail';
  return 'auth';
}
function fmt(n) { return n == null ? '—' : n.toLocaleString('en-US'); }
function fmtTime(ts) {
  if (!ts) return '—';
  return new Date(ts).toLocaleString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false });
}
