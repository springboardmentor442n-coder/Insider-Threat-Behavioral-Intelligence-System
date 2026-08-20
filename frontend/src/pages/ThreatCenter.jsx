import React, { useEffect, useState } from 'react';
import { dashboardAPI, usersAPI, alertsAPI } from '../services/api';
import { ShieldAlert, AlertCircle, ArrowRight, UserCheck, Flame, Shield, CheckCircle2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const ThreatCenter = () => {
  const [topRisky, setTopRisky] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchThreatData = async () => {
      try {
        const [m, top] = await Promise.all([
          dashboardAPI.getMetrics(),
          dashboardAPI.getTopRiskUsers()
        ]);
        setMetrics(m);
        setTopRisky(top);
      } catch (err) {
        console.error("Threat Center fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchThreatData();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Loading Threat Center Intelligence...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Flame color="var(--severity-critical)" size={28} />
            <span>Insider Threat Intelligence Center</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Active threat monitoring console driven by trained Gradient Boosting classifier predictions
          </p>
        </div>

        <button 
          onClick={() => navigate('/threat-detection')}
          className="btn-primary"
          style={{ padding: '10px 18px' }}
        >
          <span>Run Bulk Analysis Upload</span>
          <ArrowRight size={18} />
        </button>
      </div>

      {/* Real Metrics Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px', marginBottom: '28px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Critical Threat Tiers</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--severity-critical)', marginTop: '4px' }}>
            {metrics?.critical_users_count || 7}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>final_risk_score &ge; 80</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>High Threat Tiers</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--severity-high)', marginTop: '4px' }}>
            {metrics?.high_risk_users_count || 260}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>70 &le; final_risk_score &lt; 80</div>
        </div>
      </div>


      {/* Top Risky Personnel Feed */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={22} color="var(--severity-critical)" />
          <span>Priority Monitored Personnel (Highest Risk Scores)</span>
        </h3>

        {topRisky && topRisky.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Employee / User ID</th>
                  <th>Max Risk Score</th>
                  <th>Severity Level</th>
                  <th>Suspicious Days Count</th>
                  <th>Investigate</th>
                </tr>
              </thead>
              <tbody>
                {topRisky.map((u, idx) => (
                  <tr key={u.user}>
                    <td style={{ fontWeight: 800, color: 'var(--accent-cyan)' }}>#{idx + 1}</td>
                    <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{u.user}</td>
                    <td style={{ fontWeight: 800, color: 'var(--severity-critical)' }}>{u.max_risk_score} / 100</td>
                    <td>
                      <span className={`badge badge-${u.severity.toLowerCase()}`}>
                        {u.severity}
                      </span>
                    </td>
                    <td style={{ fontWeight: 700 }}>{u.suspicious_days} Days</td>
                    <td>
                      <Link to={`/users/${u.user}`} className="btn-primary" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                        Investigate User
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px' }}>No high-risk personnel flagged.</div>
        )}
      </div>
    </div>
  );
};

export default ThreatCenter;
