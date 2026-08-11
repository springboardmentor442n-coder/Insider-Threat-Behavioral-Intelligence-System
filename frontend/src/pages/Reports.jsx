import React, { useEffect, useState } from 'react';
import { reportsAPI } from '../services/api';
import { FileText, Download, ShieldCheck, CheckCircle, AlertTriangle, Users, Filter, Printer, Eye, X } from 'lucide-react';

const Reports = () => {
  const [summary, setSummary] = useState(null);
  const [activeReportTab, setActiveReportTab] = useState('summary');
  const [timeRange, setTimeRange] = useState('30d');
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true);
      try {
        const data = await reportsAPI.getSummary();
        setSummary(data);
      } catch (err) {
        console.error("Fetch report summary error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [timeRange]);

  const handleExportCSV = () => {
    if (!summary) return;
    const csvContent = `data:text/csv;charset=utf-8,` +
      `Metric,Value\n` +
      `Report Type,"${activeReportTab.toUpperCase()}"\n` +
      `Generated At,"${summary.generated_at}"\n` +
      `Total Users Monitored,${summary.total_users_monitored}\n` +
      `Behavioral Days Analyzed,${summary.total_behavioral_days_analyzed}\n` +
      `Normal Records,${summary.normal_records_count}\n` +
      `Suspicious Records,${summary.suspicious_records_count}\n` +
      `Critical Severity,${summary.critical_severity_count}\n` +
      `High Severity,${summary.high_severity_count}\n` +
      `Medium Severity,${summary.medium_severity_count}\n` +
      `Low Severity,${summary.low_severity_count}\n`;
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `insider_threat_${activeReportTab}_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Generating Intelligence Executive Report...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>Security Intelligence Reports</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Executive threat summaries, compliance audits, severity distribution reports, and export capabilities
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => setShowPreviewModal(true)} className="btn-secondary">
            <Printer size={18} />
            <span>Print Preview</span>
          </button>
          <button onClick={handleExportCSV} className="btn-primary">
            <Download size={18} />
            <span>Export CSV Audit</span>
          </button>
        </div>
      </div>

      {/* Report Navigation Tabs & Filters */}
      <div className="glass-card" style={{ padding: '16px 20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { id: 'summary', label: '1. Risk Summary' },
            { id: 'user_risk', label: '2. User Risk Report' },
            { id: 'severity', label: '3. Severity Report' },
            { id: 'alerts', label: '4. Alert Summary' },
            { id: 'analytics', label: '5. Behavioral Analytics Report' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveReportTab(tab.id)}
              className={`tab-btn ${activeReportTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="var(--text-muted)" />
          <select
            className="input-field"
            style={{ width: '140px', padding: '6px 10px', fontSize: '0.8rem' }}
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="all">Entire Dataset</option>
          </select>
        </div>
      </div>

      {/* Main Report Container */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
        <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
              {activeReportTab === 'summary' && 'Executive Insider Risk Assessment Report'}
              {activeReportTab === 'user_risk' && 'High-Risk Monitored Personnel Risk Evaluation'}
              {activeReportTab === 'severity' && 'Security Incident Severity Distribution Report'}
              {activeReportTab === 'alerts' && 'Automated Alert Queue & Triage Summary'}
              {activeReportTab === 'analytics' && 'Comprehensive Behavioral Sub-System Analytics Audit'}
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Report Generated: {new Date(summary?.generated_at).toLocaleString()} • Scope: {timeRange.toUpperCase()}
            </p>
          </div>
          <span className="badge badge-low" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={14} />
            <span>CERT r4.2 Verified</span>
          </span>
        </div>

        {/* Metric Summary Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
          <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Users Monitored</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)' }}>{summary?.total_users_monitored?.toLocaleString()}</div>
          </div>
          <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>User-Days Analyzed</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{summary?.total_behavioral_days_analyzed?.toLocaleString()}</div>
          </div>
          <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Suspicious Records</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{summary?.suspicious_records_count?.toLocaleString()}</div>
          </div>
          <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Critical Incidents</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{summary?.critical_severity_count?.toLocaleString()}</div>
          </div>
        </div>

        {/* Tab Specific Content Table */}
        <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>
          Report Data Breakdown
        </h4>
        <div style={{ overflowX: 'auto' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Employee Code</th>
                <th>Peak final_risk_score</th>
                <th>ML Classification</th>
                <th>Risk Evaluation</th>
              </tr>
            </thead>
            <tbody>
              {summary?.top_high_risk_users?.map((u, idx) => (
                <tr key={u.user}>
                  <td style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>#{idx + 1}</td>
                  <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{u.user}</td>
                  <td style={{ fontWeight: 800, color: u.max_score >= 80 ? 'var(--severity-critical)' : 'var(--accent-amber)' }}>{u.max_score} / 100</td>
                  <td style={{ fontWeight: 700, color: u.max_score >= 65 ? 'var(--severity-critical)' : 'var(--severity-low)' }}>
                    {u.max_score >= 65 ? 'SUSPICIOUS (1)' : 'NORMAL (0)'}
                  </td>
                  <td>
                    <span className={`badge badge-${u.max_score >= 85 ? 'critical' : u.max_score >= 70 ? 'high' : 'medium'}`}>
                      {u.max_score >= 85 ? 'Critical Risk' : u.max_score >= 70 ? 'High Risk' : 'Medium Risk'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Printable Preview Modal */}
      {showPreviewModal && (
        <div className="modal-overlay">
          <div className="glass-card" style={{ width: '700px', padding: '32px', borderRadius: '16px', maxHeight: '85vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>INSIDER THREAT BEHAVIORAL INTELLIGENCE SYSTEM</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Official SOC Executive Audit Report</p>
              </div>
              <button onClick={() => setShowPreviewModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={22} />
              </button>
            </div>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.6' }}>
              <p><strong>Report Reference:</strong> EXP-2026-{Math.floor(Math.random()*9000+1000)}</p>
              <p><strong>Generated Date:</strong> {new Date().toLocaleString()}</p>
              <p><strong>Classification:</strong> RESTRICTED // SOC INTERNAL USE ONLY</p>
              <hr style={{ borderColor: 'var(--border-color)', margin: '16px 0' }} />
              <p>
                This executive report summarizes behavioral telemetry from the CERT Insider Threat Dataset r4.2.
                The Gradient Boosting machine learning model classified <strong>{summary?.suspicious_records_count}</strong> user-days as suspicious with high exfiltration probability.
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
              <button onClick={() => setShowPreviewModal(false)} className="btn-secondary">Close</button>
              <button onClick={handleExportCSV} className="btn-primary">Download CSV Audit</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
