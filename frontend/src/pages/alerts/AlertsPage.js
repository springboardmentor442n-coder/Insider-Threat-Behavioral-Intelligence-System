import { useState } from 'react';
import { Bell, CheckCheck, Eye } from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner, ErrorState, EmptyState, Modal, FilterRow, SelectFilter, Pagination } from '../../components/common';
import { usePaginated } from '../../hooks/useFetch';
import { alertAPI } from '../../api/client';
import { severityBadge, fmtDT, fmtAgo, apiError } from '../../utils/helpers';
import toast from 'react-hot-toast';

const SEVERITY_OPTS = ['critical','high','medium','low','informational'].map(v => ({ value: v, label: v.charAt(0).toUpperCase()+v.slice(1) }));
const STATUS_OPTS   = ['open','acknowledged','investigating','resolved','false_positive'].map(v => ({ value: v, label: v.replace('_',' ') }));

function AlertDetailModal({ alert, open, onClose, onUpdated }) {
  const [saving, setSaving] = useState(false);

  const updateStatus = async (status) => {
    setSaving(true);
    try {
      await alertAPI.update(alert.id, { status });
      toast.success(`Alert ${status}`);
      onUpdated(); onClose();
    } catch (err) { toast.error(apiError(err)); }
    finally { setSaving(false); }
  };

  if (!alert) return null;
  return (
    <Modal open={open} onClose={onClose} title="Alert Detail" width={520}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {severityBadge(alert.severity)}
          <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{alert.alert_id}</span>
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: 6 }}>{alert.title}</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{alert.description}</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[
            ['Employee ID', alert.employee_id],
            ['Triggered',   fmtDT(alert.triggered_at)],
            ['Status',      alert.status],
            ['Acknowledged',fmtDT(alert.acknowledged_at)],
          ].map(([label, val]) => (
            <div key={label} style={{ background: 'var(--bg-surface)', borderRadius: 8, padding: '10px 12px' }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', marginTop: 3 }}>{val || '—'}</div>
            </div>
          ))}
        </div>
        {alert.status === 'open' && (
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => updateStatus('acknowledged')} disabled={saving}>
              <CheckCheck size={13} /> Acknowledge
            </button>
            <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => updateStatus('investigating')} disabled={saving}>
              <Eye size={13} /> Investigate
            </button>
            <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => updateStatus('false_positive')} disabled={saving}>
              False +ve
            </button>
          </div>
        )}
        {alert.status === 'investigating' && (
          <button className="btn btn-primary" style={{ justifyContent: 'center' }}
            onClick={() => updateStatus('resolved')} disabled={saving}>
            Mark Resolved
          </button>
        )}
      </div>
    </Modal>
  );
}

export default function AlertsPage() {
  const [selected, setSelected] = useState(null);
  const [sevFilter, setSevFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('open');
  const [days, setDays] = useState('7');

  const { data, loading, error, refetch, page, setPage, updateParams } = usePaginated(
    p => alertAPI.list(p).then(r => r.data),
    { status: 'open', days: 7 }, 50
  );

  const statusColor = { open: 'var(--risk-critical)', acknowledged: 'var(--risk-medium)',
    investigating: 'var(--risk-high)', resolved: 'var(--risk-low)', false_positive: 'var(--text-muted)' };

  return (
    <AppLayout title="Alert Management" subtitle="Monitor and respond to security alerts">
      <FilterRow>
        <SelectFilter value={sevFilter}
          onChange={v => { setSevFilter(v); updateParams({ severity: v || undefined }); }}
          options={SEVERITY_OPTS} placeholder="All Severities" />
        <SelectFilter value={statusFilter}
          onChange={v => { setStatusFilter(v); updateParams({ status: v || undefined }); }}
          options={STATUS_OPTS} placeholder="All Statuses" />
        <SelectFilter value={days}
          onChange={v => { setDays(v); updateParams({ days: Number(v) }); }}
          options={[1,7,14,30].map(d => ({ value: String(d), label: `Last ${d}d` }))} />
        <button className="btn btn-ghost" onClick={refetch}>Refresh</button>
      </FilterRow>

      <div className="card" style={{ padding: 0 }}>
        {loading ? <Spinner /> : error ? <ErrorState message={error} /> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Severity</th>
                  <th>Title</th>
                  <th>Employee</th>
                  <th>Status</th>
                  <th>Triggered</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {(Array.isArray(data) ? data : []).map(a => (
                  <tr key={a.id} style={{ cursor: 'pointer' }} onClick={() => setSelected(a)}>
                    <td><span className="mono" style={{ fontSize: '0.78rem' }}>{a.alert_id}</span></td>
                    <td>{severityBadge(a.severity)}</td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: 280 }}>
                      <span className="truncate" style={{ display: 'block' }}>{a.title}</span>
                    </td>
                    <td><span className="mono">{a.employee_id}</span></td>
                    <td>
                      <span style={{
                        fontSize: '0.72rem', padding: '2px 8px', borderRadius: 20,
                        background: `${statusColor[a.status]}18`,
                        color: statusColor[a.status],
                        fontWeight: 600, textTransform: 'capitalize',
                      }}>
                        {a.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.78rem' }}>
                      <div>{fmtAgo(a.triggered_at)}</div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{fmtDT(a.triggered_at)}</div>
                    </td>
                    <td>
                      <button className="btn btn-ghost" style={{ padding: '5px 10px', fontSize: '0.75rem' }}
                        onClick={e => { e.stopPropagation(); setSelected(a); }}>
                        <Eye size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
                {!data?.length && <tr><td colSpan={7}><EmptyState icon={Bell} message="No alerts found" /></td></tr>}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <Pagination page={page} setPage={setPage} hasMore={data?.length === 50} pageSize={50} />}
      </div>

      <AlertDetailModal alert={selected} open={!!selected}
        onClose={() => setSelected(null)} onUpdated={refetch} />
    </AppLayout>
  );
}
