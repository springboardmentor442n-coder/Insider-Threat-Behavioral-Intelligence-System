import React, { useEffect, useState } from 'react';
import { usersAPI, predictionAPI } from '../services/api';
import { HelpCircle, AlertTriangle, CheckCircle2, Sliders, Cpu, Activity } from 'lucide-react';
import { Bar } from 'react-chartjs-2';

const Explainability = () => {
  const [monitoredUsers, setMonitoredUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('USR0017');
  const [userRecords, setUserRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const [usersList, imp] = await Promise.all([
          usersAPI.getMonitoredUsers({ minRisk: 60, limit: 30 }),
          predictionAPI.getFeatureImportance()
        ]);
        setMonitoredUsers(usersList);
        setFeatureImportance(imp);
        if (usersList.length > 0) {
          setSelectedUser(usersList[0].user);
        }
      } catch (err) {
        console.error("Explainability fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    if (!selectedUser) return;
    const fetchHistory = async () => {
      try {
        const history = await usersAPI.getUserHistory(selectedUser);
        setUserRecords(history);
        if (history.length > 0) {
          // Select highest risk record by default
          const highest = [...history].sort((a, b) => b.final_risk_score - a.final_risk_score)[0];
          setSelectedRecord(highest);
        }
      } catch (err) {
        console.error("User history fetch error:", err);
      }
    };
    fetchHistory();
  }, [selectedUser]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Loading Feature-Based Model Explainability Console...</div>;
  }

  // 6 Behavioral Rules Evaluation
  const rules = selectedRecord ? [
    { name: "Off-hours Logon Spike (> 2)", val: selectedRecord.off_hours_logons, triggered: selectedRecord.off_hours_logons > 2 },
    { name: "Removable USB Connects (> 5)", val: selectedRecord.device_connects, triggered: selectedRecord.device_connects > 5 },
    { name: "Sensitive File Access (> 5)", val: selectedRecord.sensitive_file_count, triggered: selectedRecord.sensitive_file_count > 5 },
    { name: "Email Attachment Exfiltration (> 10)", val: selectedRecord.attachment_count, triggered: selectedRecord.attachment_count > 10 },
    { name: "External Email Spike (> 10)", val: selectedRecord.external_email_count, triggered: selectedRecord.external_email_count > 10 },
    { name: "Off-hours HTTP Traffic Spike (> 10)", val: selectedRecord.off_hours_http, triggered: selectedRecord.off_hours_http > 10 },
  ] : [];

  // Bar chart of top feature weights
  const barChartData = {
    labels: featureImportance.map(i => i.feature),
    datasets: [
      {
        label: 'Gradient Boosting Feature Weight',
        data: featureImportance.map(i => i.importance),
        backgroundColor: '#38bdf8',
        borderRadius: 4,
      },
    ],
  };

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <HelpCircle color="var(--accent-purple)" size={28} />
          <span>Model Explainability & Feature Contribution</span>
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Transparent risk indicator attribution based on actual feature values and Gradient Boosting weights
        </p>
      </div>

      {/* User & Record Selector Bar */}
      <div className="glass-card" style={{ padding: '20px', marginBottom: '28px', display: 'flex', gap: '20px', alignItems: 'center' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>Select Monitored User ID</label>
          <select 
            className="input-field" 
            value={selectedUser} 
            onChange={(e) => setSelectedUser(e.target.value)}
            style={{ width: '220px', fontSize: '0.85rem' }}
          >
            {monitoredUsers.map(u => (
              <option key={u.user} value={u.user}>{u.user} (Max Risk: {u.max_risk_score})</option>
            ))}
          </select>
        </div>

        {userRecords.length > 0 && (
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>Select User-Day Record</label>
            <select 
              className="input-field"
              value={selectedRecord?.id || ''}
              onChange={(e) => {
                const rec = userRecords.find(r => r.id === parseInt(e.target.value));
                if (rec) setSelectedRecord(rec);
              }}
              style={{ width: '260px', fontSize: '0.85rem' }}
            >
              {userRecords.map(r => (
                <option key={r.id} value={r.id}>
                  {r.day} — Risk: {r.final_risk_score} ({r.severity})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {selectedRecord && (
        <>
          {/* Risk Summary Header Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>ML Classification</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: selectedRecord.prediction === 1 ? 'var(--severity-critical)' : 'var(--severity-low)', marginTop: '4px' }}>
                {selectedRecord.prediction === 1 ? 'SUSPICIOUS (1)' : 'NORMAL (0)'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>Prediction Flag</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Prediction Probability</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '4px' }}>
                {(selectedRecord.prediction_probability * 100).toFixed(2)}%
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>Gradient Boosting output</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Behavioral Score</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-purple)', marginTop: '4px' }}>
                {selectedRecord.behavioral_risk_score} / 100
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>(risk_score / 6) * 100</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Final Risk Score</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-purple)', marginTop: '4px' }}>
                {selectedRecord.final_risk_score} / 100
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>0.7 * ML + 0.3 * Behavioral</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '28px' }}>
            {/* 6 Behavioral Rule Triggers Grid */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={20} color="var(--accent-amber)" />
                <span>Behavioral Rule Triggers ({selectedRecord.user} on {selectedRecord.day})</span>
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {rules.map((rule, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    backgroundColor: rule.triggered ? 'rgba(244, 63, 94, 0.12)' : 'var(--bg-secondary)',
                    border: rule.triggered ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid var(--border-color)'
                  }}>
                    <div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>{rule.name}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Recorded Value: {rule.val}</div>
                    </div>

                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      backgroundColor: rule.triggered ? 'var(--severity-critical)' : 'rgba(16, 185, 129, 0.2)',
                      color: rule.triggered ? '#fff' : 'var(--accent-emerald)'
                    }}>
                      {rule.triggered ? 'TRIGGERED (+1)' : 'NORMAL'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Model Feature Importance Weights */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={20} color="var(--accent-cyan)" />
                <span>Top Model Feature Importances</span>
              </h3>
              <div style={{ height: '300px' }}>
                <Bar data={barChartData} options={{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Explainability;
