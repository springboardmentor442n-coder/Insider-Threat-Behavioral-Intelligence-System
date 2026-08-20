import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { usersAPI } from '../services/api';
import { 
  UserCheck, 
  Clock, 
  Usb, 
  FileText, 
  Mail, 
  Globe, 
  ArrowLeft, 
  ShieldAlert, 
  BrainCircuit, 
  Activity,
  AlertTriangle
} from 'lucide-react';
import { Line, Bar } from 'react-chartjs-2';

const UserDetails = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const userId = searchParams.get('user') || 'USR0017';

  const [history, setHistory] = useState([]);
  const [selectedUserSummary, setSelectedUserSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUserData = async () => {
      setLoading(true);

      try {
        const [usersData, userHistoryData] = await Promise.all([
          usersAPI.getMonitoredUsers({ search: userId }),
          usersAPI.getUserHistory(userId)
        ]);

        console.log("User summary:", usersData);
        console.log("User history:", userHistoryData);

        // Handle monitored users response
        let users = [];

        if (Array.isArray(usersData)) {
          users = usersData;
        } else if (usersData?.users) {
          users = usersData.users;
        } else if (usersData?.data) {
          users = usersData.data;
        }

        const matchedUser =
          users.find(
            (u) =>
              String(u.user || u.username || u.id).toUpperCase() ===
              userId.toUpperCase()
          ) || users[0];

        if (matchedUser) {
          setSelectedUserSummary(matchedUser);
        }

        // History
        if (Array.isArray(userHistoryData)) {
          setHistory(userHistoryData);
        } else if (userHistoryData?.data) {
          setHistory(userHistoryData.data);
        } else {
          setHistory([]);
        }

      } catch (err) {
        console.error("User details load error:", err);
        setSelectedUserSummary(null);
        setHistory([]);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [userId]);

  if (loading) {
    return (
      <div
        style={{
          color: 'var(--text-muted)',
          textAlign: 'center',
          padding: '100px'
        }}
      >
        Loading Detailed User Behavioral Profile...
      </div>
    );
  }

  // Latest historical record
  const latestHistoryRec =
    history.length > 0 ? history[0] : {};

  // Employee-level risk values come from employee_risk_summary.csv
  // These values should be used for the profile cards.
  const latestRec = {
    ...latestHistoryRec,

    ml_risk_score:
      selectedUserSummary?.ml_risk_score ??
      latestHistoryRec.ml_risk_score ??
      0,

    behavioral_risk_score:
      selectedUserSummary?.behavioral_risk_score ??
      latestHistoryRec.behavioral_risk_score ??
      0,

    final_risk_score:
      selectedUserSummary?.display_risk_score ??
      selectedUserSummary?.risk_score ??
      latestHistoryRec.final_risk_score ??
      0,

    prediction_probability:
      selectedUserSummary?.prediction_probability ??
      latestHistoryRec.prediction_probability ??
      0,

    severity:
      selectedUserSummary?.severity ??
      latestHistoryRec.severity ??
      'Low'
  };

  // Historical Line Chart
  const historyLineData = {
    labels: history.slice().reverse().map(h => h.day),
    datasets: [
      {
        label: 'Final Risk Score (final_risk_score)',
        data: history.slice().reverse().map(h => h.final_risk_score),
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.15)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'ML Risk Score (ml_risk_score)',
        data: history.slice().reverse().map(h => h.ml_risk_score),
        borderColor: '#38bdf8',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
      }
    ],
  };

  // Behavioral Activity Breakdown Bar Chart
  const activityBarData = {
    labels: history.slice().reverse().map(h => h.day),
    datasets: [
      {
        label: 'Off-Hours Logons',
        data: history.slice().reverse().map(h => h.off_hours_logons),
        backgroundColor: '#38bdf8',
      },
      {
        label: 'USB Device Connects',
        data: history.slice().reverse().map(h => h.device_connects),
        backgroundColor: '#10b981',
      },
      {
        label: 'Sensitive Files Access',
        data: history.slice().reverse().map(h => h.sensitive_file_count),
        backgroundColor: '#f59e0b',
      },
      {
        label: 'External Emails',
        data: history.slice().reverse().map(h => h.external_email_count),
        backgroundColor: '#f43f5e',
      }
    ]
  };

  return (
    <div>
      {/* Top Header Navigation */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => navigate('/users')} className="btn-secondary" style={{ padding: '8px 12px' }}>
            <ArrowLeft size={18} />
            <span>Back to Users</span>
          </button>
          <div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <UserCheck color="var(--accent-cyan)" size={28} />
              <span>User Behavioral Profile: {userId}</span>
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '2px' }}>
              Detailed risk metrics, behavioral sub-systems, and forensic activity timeline
            </p>
          </div>
        </div>

        <button 
          onClick={() => navigate(`/investigations`)} 
          className="btn-danger"
          style={{ padding: '10px 18px' }}
        >
          <ShieldAlert size={18} />
          <span>Open Forensic Investigation</span>
        </button>
      </div>

{/* Overview Metric Cards Header */}
<div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
  <div
    style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
      gap: '16px'
    }}
  >

    {/* User ID */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">User ID</div>
      <div className="metric-value" style={{ fontFamily: 'var(--font-mono)' }}>
        {userId}
      </div>
      <div className="metric-subtitle">CERT Employee Code</div>
    </div>

    {/* Risk Status */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">Risk Status</div>
      <div style={{ marginTop: '8px' }}>
        <span className={`badge badge-${String(latestRec.severity || 'Low').toLowerCase()}`}>
          {latestRec.severity || 'Low'}
        </span>
      </div>
      <div className="metric-subtitle">Current Risk Level</div>
    </div>

    {/* Final Risk */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">Final Risk Score</div>
      <div className="metric-value">
        {Number(latestRec.final_risk_score || 0).toFixed(1)}
        <span className="metric-unit"> / 100</span>
      </div>
      <div className="metric-subtitle">final_risk_score</div>
    </div>

    {/* Behavioral Risk */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">Behavioral Risk Score</div>
      <div className="metric-value">
        {Number(latestRec.behavioral_risk_score || 0).toFixed(1)}
        <span className="metric-unit"> / 100</span>
      </div>
      <div className="metric-subtitle">behavioral_risk_score</div>
    </div>

    {/* ML Risk */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">ML Risk Score</div>
      <div className="metric-value">
        {Number(latestRec.ml_risk_score || 0).toFixed(1)}
        <span className="metric-unit"> / 100</span>
      </div>
      <div className="metric-subtitle">GB Model</div>
    </div>

    {/* ML Probability */}
    <div className="glass-card" style={{ padding: '16px' }}>
      <div className="metric-label">ML Probability</div>
      <div className="metric-value">
        {(Number(latestRec.prediction_probability || 0) * 100).toFixed(1)}%
      </div>
      <div className="metric-subtitle">prediction_probability</div>
    </div>

  </div>
</div>

    {/* Risk Status */}
    <div
      style={{
        background: 'var(--bg-secondary)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        fontWeight: 700
      }}>
        Risk Status
      </div>

      <div style={{ marginTop: '6px' }}>
        <span className={`badge badge-${String(latestRec.severity || 'Low').toLowerCase()}`}>
          {latestRec.severity || 'Low'}
        </span>
      </div>

      <div style={{
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        marginTop: '6px'
      }}>
        Active SOC Tag
      </div>
    </div>


    {/* Final Risk Score */}
    <div
      style={{
        background: 'var(--bg-secondary)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        fontWeight: 700
      }}>
        Final Risk Score
      </div>

      <div style={{
        fontSize: '1.4rem',
        fontWeight: 800,
        color: Number(latestRec.final_risk_score || 0) >= 80
          ? 'var(--severity-critical)'
          : 'var(--accent-amber)'
      }}>
        {Number(latestRec.final_risk_score || 0).toFixed(1)}
        <span style={{
          fontSize: '0.8rem',
          color: 'var(--text-dim)'
        }}>
          {' '}/ 100
        </span>
      </div>

      <div style={{
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        marginTop: '4px'
      }}>
        final_risk_score
      </div>
    </div>


    {/* Behavioral Risk Score */}
    <div
      style={{
        background: 'var(--bg-secondary)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        fontWeight: 700
      }}>
        Behavioral Risk Score
      </div>

      <div style={{
        fontSize: '1.4rem',
        fontWeight: 800,
        color: 'var(--accent-purple)'
      }}>
        {Number(latestRec.behavioral_risk_score || 0).toFixed(1)}
        <span style={{
          fontSize: '0.8rem',
          color: 'var(--text-dim)'
        }}>
          {' '}/ 100
        </span>
      </div>

      <div style={{
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        marginTop: '4px'
      }}>
        behavioral_risk_score
      </div>
    </div>


    {/* ML Risk Score */}
    <div
      style={{
        background: 'var(--bg-secondary)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        fontWeight: 700
      }}>
        ML Risk Score
      </div>

      <div style={{
        fontSize: '1.4rem',
        fontWeight: 800,
        color: 'var(--accent-cyan)'
      }}>
        {Number(latestRec.ml_risk_score || 0).toFixed(1)}
        <span style={{
          fontSize: '0.8rem',
          color: 'var(--text-dim)'
        }}>
          {' '}/ 100
        </span>
      </div>

      <div style={{
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        marginTop: '4px'
      }}>
        ml_risk_score (GB Model)
      </div>
    </div>


    {/* ML Probability */}
    <div
      style={{
        background: 'var(--bg-secondary)',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        fontWeight: 700
      }}>
        ML Probability
      </div>

      <div style={{
        fontSize: '1.4rem',
        fontWeight: 800,
        color: 'var(--accent-cyan)'
      }}>
        {(Number(latestRec.prediction_probability || 0) * 100).toFixed(1)}%
      </div>

      <div style={{
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        marginTop: '4px'
      }}>
        prediction_probability
      </div>
    </div>

  </div>
</div>

      {/* 5 Behavioral Category Sub-System Sections */}
      <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '16px' }}>Behavioral Feature Categories</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        {/* 1. Logon Behavior */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)' }}>
              <Clock size={20} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>1. Logon Behavior</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>logon_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.logon_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>logoff_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.logoff_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>off_hours_logons</span>
              <strong style={{ color: latestRec.off_hours_logons > 0 ? 'var(--severity-critical)' : 'var(--accent-emerald)' }}>
                {latestRec.off_hours_logons}
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>unique_pcs</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.unique_pcs}</strong>
            </div>
          </div>
        </div>

        {/* 2. Device Behavior */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>
              <Usb size={20} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>2. Device Behavior</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>device_connects</span>
              <strong style={{ color: latestRec.device_connects > 2 ? 'var(--severity-high)' : 'var(--text-main)' }}>
                {latestRec.device_connects}
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>device_disconnects</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.device_disconnects}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>unique_device_pcs</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.unique_device_pcs}</strong>
            </div>
          </div>
        </div>

        {/* 3. File Behavior */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)' }}>
              <FileText size={20} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>3. File Behavior</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>file_activity_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.file_activity_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>unique_file_pcs</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.unique_file_pcs}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>unique_files</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.unique_files}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>sensitive_file_count</span>
              <strong style={{ color: latestRec.sensitive_file_count > 5 ? 'var(--severity-critical)' : 'var(--text-main)' }}>
                {latestRec.sensitive_file_count}
              </strong>
            </div>
          </div>
        </div>

        {/* 4. Email Behavior */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(168, 85, 247, 0.15)', color: 'var(--accent-purple)' }}>
              <Mail size={20} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>4. Email Behavior</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>email_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.email_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>attachment_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.attachment_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>total_email_size</span>
              <strong style={{ color: 'var(--text-main)' }}>{(latestRec.total_email_size / 1024).toFixed(0)} KB</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>external_email_count</span>
              <strong style={{ color: latestRec.external_email_count > 5 ? 'var(--severity-critical)' : 'var(--text-main)' }}>
                {latestRec.external_email_count}
              </strong>
            </div>
          </div>
        </div>

        {/* 5. HTTP Behavior */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)' }}>
              <Globe size={20} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>5. HTTP Behavior</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>http_request_count</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.http_request_count}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>unique_http_urls</span>
              <strong style={{ color: 'var(--text-main)' }}>{latestRec.unique_http_urls}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>off_hours_http</span>
              <strong style={{ color: latestRec.off_hours_http > 20 ? 'var(--severity-critical)' : 'var(--text-main)' }}>
                {latestRec.off_hours_http}
              </strong>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Activity Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '28px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Historical Risk Evolution</h3>
          <div style={{ height: '260px' }}>
            <Line data={historyLineData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { color: 'var(--text-muted)' } } } }} />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Daily Anomalous Activity Breakdown</h3>
          <div style={{ height: '260px' }}>
            <Bar data={activityBarData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { color: 'var(--text-muted)' } } } }} />
          </div>
        </div>
      </div>

      {/* Daily Behavioral Log Table */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Daily Forensic Log Records</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Off-Hours Logon</th>
                <th>USB Connect</th>
                <th>Sens. Files</th>
                <th>Ext. Email</th>
                <th>Off-Hours HTTP</th>
                <th>ml_risk_score</th>
                <th>final_risk_score</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {history.map((rec) => (
                <tr key={rec.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{rec.day}</td>
                  <td>{rec.off_hours_logons}</td>
                  <td>{rec.device_connects}</td>
                  <td>{rec.sensitive_file_count}</td>
                  <td>{rec.external_email_count}</td>
                  <td>{rec.off_hours_http}</td>
                  <td style={{ fontWeight: 600 }}>{rec.ml_risk_score}</td>
                  <td style={{ fontWeight: 800, color: rec.final_risk_score >= 75 ? 'var(--severity-critical)' : 'var(--accent-cyan)' }}>
                    {rec.final_risk_score}
                  </td>
                  <td>
                    <span className={`badge badge-${rec.severity.toLowerCase()}`}>{rec.severity}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UserDetails;
