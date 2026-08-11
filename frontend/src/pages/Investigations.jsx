import React, { useEffect, useState } from 'react';
import { investigationsAPI } from '../services/api';
import { FileSearch, Plus, User, Tag, Clock, Send, ShieldAlert, CheckCircle2, Lock, UserCheck, X } from 'lucide-react';

const Investigations = () => {
  const [investigations, setInvestigations] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);

  // Create form state
  const [newCaseData, setNewCaseData] = useState({
    title: '',
    user: 'USR0017',
    severity: 'Critical',
    risk_score: 90,
    assigned_analyst: 'SOC Security Analyst',
    risk_factors: 'Off-Hours Logon, USB Insertion, Sensitive File Access'
  });

  const fetchInvestigations = async () => {
    setLoading(true);
    try {
      const data = await investigationsAPI.getInvestigations();
      setInvestigations(data);
      if (data.length > 0 && !selectedCase) {
        setSelectedCase(data[0]);
      }
    } catch (err) {
      console.error("Fetch investigations error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, []);

  const handleAddNote = async () => {
    if (!newNote.trim() || !selectedCase) return;
    try {
      const updated = await investigationsAPI.updateInvestigation(selectedCase.id, { notes: newNote });
      setSelectedCase(updated);
      setNewNote('');
      fetchInvestigations();
    } catch (err) {
      console.error("Add note error:", err);
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (!selectedCase) return;
    try {
      const updated = await investigationsAPI.updateInvestigation(selectedCase.id, { status: newStatus });
      setSelectedCase(updated);
      fetchInvestigations();
    } catch (err) {
      console.error("Update investigation status error:", err);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const created = await investigationsAPI.createInvestigation(newCaseData);
      setSelectedCase(created);
      setShowCreateModal(false);
      fetchInvestigations();
    } catch (err) {
      console.error("Create investigation error:", err);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>Incident Investigation Workbench</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Forensic incident case management, behavioral risk factor tracking, and analyst containment actions
          </p>
        </div>

        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus size={18} />
          <span>New Incident Case</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        {/* Cases List */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileSearch size={18} color="var(--accent-cyan)" />
            <span>Active Investigation Cases</span>
          </h3>

          {loading ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>Loading Cases...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {investigations.map((inv) => (
                <div
                  key={inv.id}
                  onClick={() => setSelectedCase(inv)}
                  style={{
                    padding: '14px',
                    borderRadius: '8px',
                    backgroundColor: selectedCase?.id === inv.id ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-secondary)',
                    border: selectedCase?.id === inv.id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-main)', fontSize: '0.85rem' }}>#{inv.id} • {inv.user}</span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      backgroundColor: inv.status === 'Contained' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(56, 189, 248, 0.15)',
                      color: inv.status === 'Contained' ? 'var(--severity-critical)' : 'var(--accent-cyan)'
                    }}>
                      {inv.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>{inv.title}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>Created: {inv.created_date}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Case Detail Panel */}
        {selectedCase ? (
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>Case #{selectedCase.id}: {selectedCase.title}</h3>
                <span className={`badge badge-${selectedCase.severity.toLowerCase()}`}>{selectedCase.severity}</span>
              </div>
              <div style={{ display: 'flex', gap: '20px', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px', flexWrap: 'wrap' }}>
                <span>Subject User: <strong style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{selectedCase.user}</strong></span>
                <span>Risk Score: <strong style={{ color: 'var(--severity-critical)' }}>{selectedCase.risk_score} / 100</strong></span>
                <span>Created Date: <strong style={{ color: 'var(--text-main)' }}>{selectedCase.created_date}</strong></span>
                <span>Assigned Analyst: <strong style={{ color: 'var(--accent-purple)' }}>{selectedCase.assigned_analyst}</strong></span>
              </div>
            </div>

            {/* Investigation Actions Toolbar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-secondary)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)' }}>Case Status:</span>
                <select
                  value={selectedCase.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  className="input-field"
                  style={{ width: '150px', padding: '4px 8px', fontSize: '0.8rem' }}
                >
                  <option value="New">New</option>
                  <option value="Investigating">Investigating</option>
                  <option value="Contained">Contained</option>
                  <option value="Resolved">Resolved</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => handleStatusChange('Contained')}
                  className="btn-danger"
                  style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                >
                  <Lock size={14} />
                  <span>Contain Subject User</span>
                </button>
              </div>
            </div>

            {/* Risk Factors */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Flagged Behavioral Risk Factors
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {selectedCase.risk_factors?.split(',').map((factor, idx) => (
                  <span key={idx} style={{ padding: '4px 10px', borderRadius: '12px', background: 'rgba(244, 63, 94, 0.15)', color: 'var(--severity-critical)', fontSize: '0.75rem', fontWeight: 600, border: '1px solid rgba(244, 63, 94, 0.3)' }}>
                    {factor.trim()}
                  </span>
                ))}
              </div>
            </div>

            {/* Activity Forensic Timeline */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Forensic Activity Timeline
              </div>
              <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
                  <Clock size={16} color="var(--accent-cyan)" />
                  <span><strong>18:45:00</strong> — User logged on outside working hours (off_hours_logons = 4)</span>
                </div>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
                  <Clock size={16} color="var(--accent-amber)" />
                  <span><strong>19:12:30</strong> — USB storage device attached (device_connects = 7)</span>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <Clock size={16} color="var(--severity-critical)" />
                  <span><strong>19:35:10</strong> — Copied 19 sensitive files (.pdf, .doc) (sensitive_file_count = 19)</span>
                </div>
              </div>
            </div>

            {/* Analyst Work Log Notes */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Analyst Work Log Notes
              </div>
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)', minHeight: '120px', whiteSpace: 'pre-line', fontSize: '0.85rem', color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>
                {selectedCase.notes || 'No work notes logged yet.'}
              </div>
            </div>

            {/* Add Note Input */}
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                className="input-field"
                placeholder="Append new investigation note..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
              />
              <button onClick={handleAddNote} className="btn-primary">
                <Send size={16} />
                <span>Append Note</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Select an investigation case to inspect details.
          </div>
        )}
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="glass-card" style={{ width: '500px', padding: '28px', borderRadius: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>Open New Incident Case</h3>
              <button onClick={() => setShowCreateModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>CASE TITLE</label>
                <input
                  type="text"
                  className="input-field"
                  value={newCaseData.title}
                  onChange={(e) => setNewCaseData(prev => ({ ...prev, title: e.target.value }))}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>USER ID</label>
                  <input
                    type="text"
                    className="input-field"
                    value={newCaseData.user}
                    onChange={(e) => setNewCaseData(prev => ({ ...prev, user: e.target.value }))}
                    required
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>SEVERITY</label>
                  <select
                    className="input-field"
                    value={newCaseData.severity}
                    onChange={(e) => setNewCaseData(prev => ({ ...prev, severity: e.target.value }))}
                  >
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>RISK FACTORS</label>
                <input
                  type="text"
                  className="input-field"
                  value={newCaseData.risk_factors}
                  onChange={(e) => setNewCaseData(prev => ({ ...prev, risk_factors: e.target.value }))}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary">Create Case</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Investigations;
