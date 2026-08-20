import React, { useEffect, useState } from 'react';
import { reportsAPI } from '../services/api';
import { FileText, Download, ShieldCheck, CheckCircle, AlertTriangle, Users, Filter, Printer, Eye, X, Bell, FileSearch, TrendingUp, BarChart3 } from 'lucide-react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

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
        const data = await reportsAPI.getSummary(timeRange);
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
      `Normal Users,${summary.normal_users_count || 0}\n` +
      `Suspicious Users,${summary.suspicious_users_count || 0}\n` +
      `High-Risk Users,${summary.high_risk_users_count || 0}\n` +
      `Medium-Risk Users,${summary.medium_risk_users_count || 0}\n` +
      `Low-Risk Users,${summary.low_risk_users_count || 0}\n` +
      `Total Alerts,${summary.total_alerts || 0}\n` +
      `Open Investigations,${summary.open_investigations || 0}\n` +
      `Resolved Investigations,${summary.resolved_investigations || 0}\n`;
    
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

  // 1. Risk Distribution Bar Chart Data
  const riskDistData = {
    labels: summary?.risk_distribution?.labels || ['0-20 (Normal)', '21-40 (Low)', '41-60 (Medium)', '61-80 (High)', '81-100 (Critical)'],
    datasets: [
      {
        label: 'Monitored Dataset Records',
        data: summary?.risk_distribution?.counts || [0, 0, 0, 0, 0],
        backgroundColor: ['rgba(16, 185, 129, 0.7)', 'rgba(56, 189, 248, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(249, 115, 22, 0.8)', 'rgba(244, 63, 94, 0.9)'],
        borderRadius: 6,
      }
    ]
  };

  // 2. Threat Trend Line Chart Data
  const threatTrendData = {
    labels: summary?.threat_trend?.map(t => t.day) || [],
    datasets: [
      {
        label: 'Average final_risk_score',
        data: summary?.threat_trend?.map(t => t.avg_risk_score) || [],
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.12)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Suspicious Predictions',
        data: summary?.threat_trend?.map(t => t.suspicious_count) || [],
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.12)',
        fill: false,
        tension: 0.4,
      }
    ]
  };

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

      {/* Report Filters Header */}
      <div className="glass-card" style={{ padding: '16px 20px', marginBottom: '24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>


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

      {/* Dynamic Statistics Grid (Rule 11) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '14px', marginBottom: '28px' }}>
        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Total Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>{summary?.total_users_monitored?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Monitored personnel</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Total Analysed User-Days</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '2px' }}>{summary?.total_behavioral_days_analyzed?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Evaluated days</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Normal Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-low)', marginTop: '2px' }}>{summary?.normal_users_count?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>prediction = 0</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Suspicious Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)', marginTop: '2px' }}>{summary?.suspicious_users_count?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>prediction = 1</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>High-Risk Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-high)', marginTop: '2px' }}>{summary?.high_risk_users_count?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>High severity</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Medium-Risk Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-medium)', marginTop: '2px' }}>{summary?.medium_risk_users_count?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Medium severity</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Low-Risk Users</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-low)', marginTop: '2px' }}>{summary?.low_risk_users_count?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Low severity</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Total Alerts</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-purple)', marginTop: '2px' }}>{summary?.total_alerts?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Generated alerts</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Open Investigations</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--severity-critical)', marginTop: '2px' }}>{summary?.open_investigations?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Active cases</div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Resolved Investigations</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '2px' }}>{summary?.resolved_investigations?.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Closed cases</div>
        </div>
      </div>

      {/* Report Charts Section (Rule 12) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '28px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={18} color="var(--accent-cyan)" />
            <span>Risk Score Distribution (Backend Data)</span>
          </h3>
          <div style={{ height: '240px' }}>
            <Bar data={riskDistData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={18} color="var(--severity-critical)" />
            <span>Threat Trend (Backend Aggregation)</span>
          </h3>
          <div style={{ height: '240px' }}>
            <Line data={threatTrendData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { color: 'var(--text-muted)' } } } }} />
          </div>
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
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Report Generated: {summary?.generated_at} • Scope: {timeRange.toUpperCase()}
            </p>
          </div>
          <span className="badge badge-low" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={14} />
            <span>CERT r4.2 Verified Data</span>
          </span>
        </div>

        {/* Tab Specific Content Table */}
        <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>
          High-Risk Personnel Evaluation Breakdown
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
              <p><strong>Report Reference:</strong> EXP-2026-AUDIT</p>
              <p><strong>Generated Date:</strong> {summary?.generated_at}</p>
              <p><strong>Classification:</strong> RESTRICTED // SOC INTERNAL USE ONLY</p>
              <hr style={{ borderColor: 'var(--border-color)', margin: '16px 0' }} />
              <p>
                This executive report summarizes behavioral telemetry from the CERT Insider Threat Dataset r4.2.
                The Gradient Boosting machine learning model classified <strong>{summary?.suspicious_records_count}</strong> user-days as suspicious with high exfiltration probability across <strong>{summary?.total_users_monitored}</strong> monitored users.
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

