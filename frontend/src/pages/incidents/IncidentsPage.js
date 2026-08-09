// ── Incidents Page ────────────────────────────────────────────────────────────
import { useState } from 'react';
import { AlertTriangle, Eye, Plus, Clock } from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner, ErrorState, EmptyState, Modal, FilterRow, SelectFilter, Pagination, SectionHeader } from '../../components/common';
import { usePaginated, useFetch } from '../../hooks/useFetch';
import api, { incidentAPI } from '../../api/client';
import { severityBadge, fmtDT, fmtAgo, apiError } from '../../utils/helpers';
import toast from 'react-hot-toast';

const SEV_OPTS = ['critical', 'high', 'medium', 'low'].map(v => ({ value: v, label: v.charAt(0).toUpperCase() + v.slice(1) }));
const STATUS_OPTS = ['open', 'in_progress', 'resolved', 'closed'].map(v => ({ value: v, label: v.replace('_', ' ') }));

function TimelineModal({ incidentId, open, onClose }) {
  const { data, loading } = useFetch(
    () => incidentAPI.timeline(incidentId).then(r => r.data), [incidentId]
  );
  return (
    <Modal open={open} onClose={onClose} title="Activity Timeline" width={600}>
      {loading ? <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div> : (
        <div>
          {(data?.timeline || []).length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 24 }}>No activity in timeline window</div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 450, overflowY: 'auto' }}>
            {(data?.timeline || []).map((ev, i) => (
              <div key={i} style={{
                display: 'flex', gap: 12, padding: '10px 12px', borderRadius: 8,
                background: ev.is_suspicious ? 'var(--risk-critical-bg)' : 'var(--bg-surface)',
                border: `1px solid ${ev.is_suspicious ? 'var(--risk-critical)' : 'var(--border)'}`,
              }}>
                <div style={{ width: 3, borderRadius: 2, flexShrink: 0, background: ev.is_outside_hours ? 'var(--risk-high)' : 'var(--border-light)' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {ev.activity_type?.replace(/_/g, ' ')}
                    </span>
                    <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {ev.resource && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{ev.resource}</div>}
                  <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                    {ev.is_suspicious && <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>suspicious</span>}
                    {ev.is_outside_hours && <span className="badge badge-high" style={{ fontSize: '0.65rem' }}>off-hours</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Modal>
  );
}

function CreateIncidentModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({ title: '', description: '', severity: 'high', employee_id: '' });
  const [saving, setSaving] = useState(false);

  const handle = async e => {
    e.preventDefault(); setSaving(true);
    try {
      await incidentAPI.create({ ...form, employee_id: form.employee_id ? Number(form.employee_id) : null });
      toast.success('Incident created'); onCreated(); onClose();
      setForm({ title: '', description: '', severity: 'high', employee_id: '' });
    } catch (err) { toast.error(apiError(err)); }
    finally { setSaving(false); }
  };

  return (
    <Modal open={open} onClose={onClose} title="Open New Incident">
      <form onSubmit={handle}>
        <div className="form-group">
          <label className="form-label">Title</label>
          <input className="form-input" required placeholder="Suspicious data exfiltration attempt"
            value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
        </div>
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea className="form-input" rows={3} placeholder="Describe the incident…"
            value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            style={{ resize: 'vertical' }} />
        </div>
        <div className="form-group">
          <label className="form-label">Severity</label>
          <select className="form-input" value={form.severity}
            onChange={e => setForm(f => ({ ...f, severity: e.target.value }))}>
            {SEV_OPTS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Employee ID (optional)</label>
          <input className="form-input" placeholder="123"
            value={form.employee_id} onChange={e => setForm(f => ({ ...f, employee_id: e.target.value }))} />
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create Incident'}</button>
        </div>
      </form>
    </Modal>
  );
}

export function IncidentsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [timeline, setTimeline] = useState(null);
  const [sevFilter, setSevFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('open');

  const { data, loading, error, refetch, page, setPage, updateParams } = usePaginated(
    p => incidentAPI.list(p).then(r => r.data), { status: 'open' }, 20
  );

  const statusColor = {
    open: 'var(--risk-critical)', in_progress: 'var(--risk-high)',
    resolved: 'var(--risk-low)', closed: 'var(--text-muted)'
  };

  return (
    <AppLayout title="Incident Management" subtitle="Threat investigation and case management">
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 20 }}>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={14} /> Open Incident
        </button>
      </div>

      <FilterRow>
        <SelectFilter value={sevFilter}
          onChange={v => { setSevFilter(v); updateParams({ severity: v || undefined }); }}
          options={SEV_OPTS} placeholder="All Severities" />
        <SelectFilter value={statusFilter}
          onChange={v => { setStatusFilter(v); updateParams({ status: v || undefined }); }}
          options={STATUS_OPTS} placeholder="All Statuses" />
        <button className="btn btn-ghost" onClick={refetch}>Refresh</button>
      </FilterRow>

      <div className="card" style={{ padding: 0 }}>
        {loading ? <Spinner /> : error ? <ErrorState message={error} /> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>ID</th><th>Title</th><th>Severity</th><th>Status</th><th>Employee</th><th>Opened</th><th></th></tr>
              </thead>
              <tbody>
                {(Array.isArray(data) ? data : []).map(inc => (
                  <tr key={inc.id}>
                    <td><span className="mono" style={{ fontSize: '0.78rem' }}>{inc.incident_id}</span></td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: 280 }}>
                      <span className="truncate" style={{ display: 'block' }}>{inc.title}</span>
                    </td>
                    <td>{severityBadge(inc.severity)}</td>
                    <td>
                      <span style={{
                        fontSize: '0.72rem', padding: '2px 8px', borderRadius: 20, fontWeight: 600,
                        background: `${statusColor[inc.status]}18`, color: statusColor[inc.status],
                        textTransform: 'capitalize',
                      }}>{inc.status?.replace('_', ' ')}</span>
                    </td>
                    <td><span className="mono">{inc.employee_id || '—'}</span></td>
                    <td style={{ fontSize: '0.78rem' }}>
                      <div>{fmtAgo(inc.opened_at)}</div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{fmtDT(inc.opened_at)}</div>
                    </td>
                    <td>
                      <button className="btn btn-ghost" style={{ padding: '5px 10px', fontSize: '0.75rem' }}
                        onClick={() => setTimeline(inc.id)}>
                        <Clock size={12} /> Timeline
                      </button>
                    </td>
                  </tr>
                ))}
                {!data?.length && <tr><td colSpan={7}><EmptyState icon={AlertTriangle} message="No incidents found" /></td></tr>}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <Pagination page={page} setPage={setPage} hasMore={data?.length === 20} pageSize={20} />}
      </div>

      <CreateIncidentModal open={showCreate} onClose={() => setShowCreate(false)} onCreated={refetch} />
      {timeline && <TimelineModal incidentId={timeline} open={!!timeline} onClose={() => setTimeline(null)} />}
    </AppLayout>
  );
}

// ── Activities Page ────────────────────────────────────────────────────────────
export function ActivitiesPage() {
  const [typeFilter, setTypeFilter] = useState('');
  const [suspOnly, setSuspOnly] = useState(false);
  const [uploadType, setUploadType] = useState('logon');
  const [uploading, setUploading] = useState(false);

  const { data, loading, error, refetch, page, setPage, updateParams } = usePaginated(
    p => import('../../api/client').then(m => m.activityAPI.list(p).then(r => r.data)),
    { days: 7 }, 50
  );

  const handleUpload = async (e) => {
    const file = e.target.files[0]; if (!file) return;
    setUploading(true);
    try {
      const { activityAPI } = await import('../../api/client');
      await activityAPI.uploadCERT(uploadType, file);
      toast.success(`CERT ${uploadType}.csv upload queued`);
    } catch (err) { toast.error(apiError(err)); }
    finally { setUploading(false); e.target.value = ''; }
  };

  const ACT_OPTS = [
    'login', 'logout', 'file_download', 'file_upload', 'file_delete',
    'email_send', 'usb_connect', 'data_transfer', 'privilege_change',
  ].map(v => ({ value: v, label: v.replace(/_/g, ' ') }));

  return (
    <AppLayout title="Activity Monitoring" subtitle="Real-time employee activity log analysis">
      {/* CERT Upload */}
      <div className="card" style={{ marginBottom: 20 }}>
        <SectionHeader title="CERT Dataset Upload" subtitle="Upload r4.2 CSV files for bulk ingestion" />
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <SelectFilter value={uploadType} onChange={setUploadType}
            options={['logon', 'file', 'device', 'email', 'http'].map(v => ({ value: v, label: `${v}.csv` }))} />
          <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
            {uploading ? 'Uploading…' : 'Upload CSV'}
            <input type="file" accept=".csv" onChange={handleUpload} hidden disabled={uploading} />
          </label>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Dataset: kilthub.cmu.edu → CERT r4.2
          </span>
        </div>
      </div>

      <FilterRow>
        <SelectFilter value={typeFilter}
          onChange={v => { setTypeFilter(v); updateParams({ activity_type: v || undefined }); }}
          options={ACT_OPTS} placeholder="All Types" />
        <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input type="checkbox" checked={suspOnly} onChange={e => { setSuspOnly(e.target.checked); updateParams({ is_suspicious: e.target.checked || undefined }); }} />
          Suspicious only
        </label>
        <button className="btn btn-ghost" onClick={refetch}>Refresh</button>
      </FilterRow>

      <div className="card" style={{ padding: 0 }}>
        {loading ? <Spinner /> : error ? <ErrorState message={error} /> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Timestamp</th><th>Employee</th><th>Activity</th><th>Resource</th><th>Source IP</th><th>Bytes</th><th>Flags</th></tr>
              </thead>
              <tbody>
                {(Array.isArray(data) ? data : []).map(a => (
                  <tr key={a.id} style={{ background: a.is_suspicious ? 'rgba(255,59,92,0.04)' : undefined }}>
                    <td className="mono" style={{ fontSize: '0.78rem' }}>{fmtDT(a.timestamp)}</td>
                    <td><span className="mono">{a.employee_id}</span></td>
                    <td style={{ color: 'var(--text-primary)' }}>{a.activity_type?.replace(/_/g, ' ')}</td>
                    <td style={{ maxWidth: 200 }}>
                      <span className="truncate mono" style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {a.resource || '—'}
                      </span>
                    </td>
                    <td><span className="mono" style={{ fontSize: '0.78rem' }}>{a.source_ip || '—'}</span></td>
                    <td className="mono" style={{ fontSize: '0.78rem' }}>
                      {a.bytes_transferred ? `${(a.bytes_transferred / 1048576).toFixed(1)}MB` : '—'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                        {a.is_suspicious && <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>suspicious</span>}
                        {a.is_outside_hours && <span className="badge badge-high" style={{ fontSize: '0.65rem' }}>off-hours</span>}
                      </div>
                    </td>
                  </tr>
                ))}
                {!data?.length && <tr><td colSpan={7}><EmptyState message="No activities found" /></td></tr>}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <Pagination page={page} setPage={setPage} hasMore={data?.length === 50} pageSize={50} />}
      </div>
    </AppLayout>
  );
}

export function ReportsPage() {
  const handleExport = async (type, format) => {
    toast.loading(`Generating ${format.toUpperCase()} report...`, { id: 'report-export' });
    try {
      if (format === 'csv') {
        const response = await api.get(`/reports/export/csv?report_type=${type}`, {
          responseType: 'blob',
        });
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ueba_report_${type}_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        toast.success(`${type.toUpperCase()} Excel/CSV exported successfully`, { id: 'report-export' });
      } else if (format === 'pdf') {
        const response = await api.get(`/reports/export/pdf?report_type=${type}`);
        const printWindow = window.open('', '_blank');
        if (printWindow) {
          printWindow.document.write(response.data);
          printWindow.document.close();
          toast.success(`PDF Print window opened for ${type.toUpperCase()}`, { id: 'report-export' });
        } else {
          toast.error('Popup blocked. Please allow popups to view PDF reports.', { id: 'report-export' });
        }
      }
    } catch (err) {
      toast.error(`Export failed: ${apiError(err)}`, { id: 'report-export' });
    }
  };

  const reports = [
    { title: 'Insider Threat Report', desc: 'Comprehensive analysis of all triggered alerts', icon: '🛡️', type: 'alerts' },
    { title: 'Risk Assessment Report', desc: 'Employee risk scores and risk categorization leaderboard', icon: '⚠️', type: 'employees' },
    { title: 'Investigation Report', desc: 'Open and resolved security incident summaries', icon: '🔍', type: 'incidents' },
  ];

  return (
    <AppLayout title="Reports & Export" subtitle="Generate and download security intelligence reports">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 16 }}>
        {reports.map(r => (
          <div key={r.title} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%' }}>
            <div>
              <div style={{ fontSize: '2rem', marginBottom: 12 }}>{r.icon}</div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: 6 }}>{r.title}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 16 }}>{r.desc}</div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button className="btn btn-primary" style={{ fontSize: '0.75rem', padding: '6px 12px', flex: 1 }}
                onClick={() => handleExport(r.type, 'pdf')}>PDF Report</button>
              <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '6px 12px', flex: 1 }}
                onClick={() => handleExport(r.type, 'csv')}>Excel / CSV</button>
            </div>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}

export default IncidentsPage;
