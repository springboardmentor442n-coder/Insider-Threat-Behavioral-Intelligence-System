import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { alertsAPI } from '../services/api';
import { Bell, ShieldAlert, CheckCircle, Clock, AlertTriangle, Eye, X, FileSearch } from 'lucide-react';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await alertsAPI.getAlerts({ status: statusFilter, severity: severityFilter });
      setAlerts(data);
    } catch (err) {
      console.error("Fetch alerts error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const handleStatusChange = async (alertId, newStatus) => {
    try {
      await alertsAPI.updateStatus(alertId, newStatus);
      if (selectedAlert && selectedAlert.id === alertId) {
        setSelectedAlert(prev => ({ ...prev, status: newStatus }));
      }
      fetchAlerts();
    } catch (err) {
      console.error("Update status error:", err);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>Security Alert Triage Center</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            SOC incident response queue & automated threat alert classification
          </p>
        </div>

        {/* Severity Filter Pills & Status Dropdown */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: '6px', backgroundColor: 'var(--bg-secondary)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            {['', 'Critical', 'High', 'Medium', 'Low'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`tab-btn ${severityFilter === sev ? 'active' : ''}`}
                style={{ padding: '6px 12px', fontSize: '0.75rem' }}
              >
                {sev || 'All Severities'}
              </button>
            ))}
          </div>

          <select 
            className="input-field" 
            style={{ width: '160px', padding: '6px 10px', fontSize: '0.8rem' }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
            <option value="Dismissed">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Loading Security Alerts...</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>User</th>
                  <th>Severity</th>
                  <th>Risk Score</th>
                  <th>Detected Time</th>
                  <th>Status</th>
                  <th>Action / Triage</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alt) => (
                  <tr key={alt.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700 }}>#ALT-{alt.id}</td>
                    <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{alt.user}</td>
                    <td>
                      <span className={`badge badge-${alt.severity.toLowerCase()}`}>{alt.severity}</span>
                    </td>
                    <td style={{ fontWeight: 800, color: alt.risk_score >= 80 ? 'var(--severity-critical)' : 'var(--accent-amber)' }}>
                      {alt.risk_score} / 100
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {alt.detected_time ? new Date(alt.detected_time).toLocaleString() : alt.day}
                    </td>
                    <td>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: alt.status === 'New' ? 'rgba(244, 63, 94, 0.15)' : alt.status === 'Investigating' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                        color: alt.status === 'New' ? 'var(--severity-critical)' : alt.status === 'Investigating' ? 'var(--severity-medium)' : 'var(--severity-low)'
                      }}>
                        {alt.status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <button
                          onClick={() => setSelectedAlert(alt)}
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem', gap: '4px' }}
                        >
                          <Eye size={14} />
                          <span>Inspect</span>
                        </button>
                        <select
                          value={alt.status}
                          onChange={(e) => handleStatusChange(alt.id, e.target.value)}
                          className="input-field"
                          style={{ padding: '4px 8px', fontSize: '0.75rem', width: '130px' }}
                        >
                          <option value="New">New</option>
                          <option value="Investigating">Investigating</option>
                          <option value="Resolved">Resolved</option>
                          <option value="Dismissed">Dismissed</option>
                        </select>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div className="modal-overlay">
          <div className="glass-card" style={{ width: '600px', padding: '28px', borderRadius: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldAlert color="var(--severity-critical)" />
                  <span>Alert #ALT-{selectedAlert.id} Details</span>
                </h3>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Subject User: <strong style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{selectedAlert.user}</strong>
                </div>
              </div>
              <button onClick={() => setSelectedAlert(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={22} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>{selectedAlert.title}</div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>{selectedAlert.description}</p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Severity</span>
                  <div style={{ marginTop: '4px' }}>
                    <span className={`badge badge-${selectedAlert.severity.toLowerCase()}`}>{selectedAlert.severity}</span>
                  </div>
                </div>
                <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Risk Score</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--severity-critical)', marginTop: '2px' }}>{selectedAlert.risk_score} / 100</div>
                </div>
                <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</span>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-cyan)', marginTop: '2px' }}>{selectedAlert.status}</div>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
              <button
                onClick={() => {
                  navigate(`/investigations`);
                  setSelectedAlert(null);
                }}
                className="btn-primary"
              >
                <FileSearch size={16} />
                <span>Escalate to Investigation</span>
              </button>

              <button onClick={() => setSelectedAlert(null)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;
