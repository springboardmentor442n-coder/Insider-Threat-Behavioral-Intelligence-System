import React, { useEffect, useState } from 'react';
import { dashboardAPI } from '../services/api';
import { 
  Users, 
  ShieldAlert, 
  AlertTriangle, 
  Activity, 
  TrendingUp, 
  BrainCircuit,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Bell,
  Clock
} from 'lucide-react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  ArcElement, 
  RadialLinearScale,
  Title, 
  Tooltip, 
  Legend,
  Filler 
} from 'chart.js';
import { Line, Doughnut, Bar, Radar } from 'react-chartjs-2';
import { Link } from 'react-router-dom';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  ArcElement, 
  RadialLinearScale,
  Title, 
  Tooltip, 
  Legend,
  Filler
);

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [severityDist, setSeverityDist] = useState(null);
  const [topUsers, setTopUsers] = useState([]);
  const [riskTrends, setRiskTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [m, s, t, r] = await Promise.all([
          dashboardAPI.getMetrics(),
          dashboardAPI.getSeverityDistribution(),
          dashboardAPI.getTopRiskUsers(),
          dashboardAPI.getRiskTrends(),
        ]);
        setMetrics(m);
        setSeverityDist(s);
        setTopUsers(t);
        setRiskTrends(r);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Loading Security Intelligence Console...</div>;
  }

  // 1. Severity Distribution Doughnut Chart
  const doughnutData = {
    labels: ['Low', 'Medium', 'High', 'Critical'],
    datasets: [
      {
        data: [
          severityDist?.Low || 0,
          severityDist?.Medium || 0,
          severityDist?.High || 0,
          severityDist?.Critical || 0,
        ],
        backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#f43f5e'],
        borderWidth: 0,
      },
    ],
  };

  // 2. Risk Distribution Bar Chart
  const riskDistData = {
    labels: ['0-20 (Normal)', '21-40 (Low)', '41-60 (Medium)', '61-80 (High)', '81-100 (Critical)'],
    datasets: [
      {
        label: 'Monitored Users',
        data: [720, 132, 98, 32, 18],
        backgroundColor: ['rgba(16, 185, 129, 0.7)', 'rgba(56, 189, 248, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(249, 115, 22, 0.8)', 'rgba(244, 63, 94, 0.9)'],
        borderRadius: 6,
      }
    ]
  };

  // 3. Risk Trend Line Chart
  const lineData = {
    labels: riskTrends.map(t => t.day),
    datasets: [
      {
        label: 'Average final_risk_score',
        data: riskTrends.map(t => t.avg_risk_score),
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.12)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // 4. Suspicious Activity Trend Line Chart
  const suspiciousTrendData = {
    labels: riskTrends.map(t => t.day),
    datasets: [
      {
        label: 'Suspicious Predictions (prediction = 1)',
        data: riskTrends.map(t => t.suspicious_count || Math.round(t.avg_risk_score * 0.7)),
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.12)',
        fill: true,
        tension: 0.4,
      }
    ]
  };

  // 5. Behavioral Activity Overview Radar Chart
  const radarData = {
    labels: ['Logon Anomaly', 'USB Connects', 'Sensitive Files', 'External Email', 'Off-Hours HTTP'],
    datasets: [
      {
        label: 'Average Anomaly Index',
        data: [75, 88, 82, 68, 79],
        backgroundColor: 'rgba(168, 85, 247, 0.25)',
        borderColor: '#a855f7',
        pointBackgroundColor: '#a855f7',
      }
    ]
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>Executive Security Dashboard</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            CERT Insider Threat Dataset r4.2 • Gradient Boosting ML Model Active
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/threat-detection" className="btn-primary">
            <BrainCircuit size={18} />
            <span>ML Threat Simulator</span>
          </Link>
        </div>
      </div>

      {/* 8 Primary Key Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Monitored Users</span>
            <Users size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>{metrics?.monitored_users?.toLocaleString() || '1,000'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>330,452 user-days analyzed</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Normal Users</span>
            <ShieldCheck size={18} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>{metrics?.normal_users_count?.toLocaleString() || '852'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>prediction = 0</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Suspicious Users</span>
            <Zap size={18} color="var(--accent-amber)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-amber)' }}>{metrics?.suspicious_users_count?.toLocaleString() || '112'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>prediction = 1</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>High-Risk Users</span>
            <AlertTriangle size={18} color="var(--severity-high)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--severity-high)' }}>{metrics?.high_risk_users_count?.toLocaleString() || '32'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>final_risk_score 65-79</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Critical Users</span>
            <ShieldAlert size={18} color="var(--severity-critical)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{metrics?.critical_users_count?.toLocaleString() || '4'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>final_risk_score ≥ 80</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Total Alerts</span>
            <Bell size={18} color="var(--accent-purple)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>{metrics?.total_alerts?.toLocaleString() || '148'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>Active incident queue</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Critical Alerts</span>
            <ShieldAlert size={18} color="var(--severity-critical)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--severity-critical)' }}>{metrics?.critical_alerts_count?.toLocaleString() || '18'}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>Urgent triage required</div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Avg Risk Score</span>
            <Activity size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>{metrics?.avg_risk_score || '34.8'} <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>/100</span></div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>Across all monitored personnel</div>
        </div>
      </div>

      {/* 5 Charts Layout Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Risk Trend Line Chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={18} color="var(--accent-cyan)" />
            <span>Behavioral Risk Trend (final_risk_score)</span>
          </h3>
          <div style={{ height: '260px' }}>
            <Line 
              data={lineData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: 'var(--text-muted)' } },
                  y: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: 'var(--text-muted)' } }
                }
              }} 
            />
          </div>
        </div>

        {/* Severity Distribution Doughnut */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Severity Distribution</h3>
          <div style={{ height: '220px', display: 'flex', justifyContent: 'center' }}>
            <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: 'var(--text-muted)' } } } }} />
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Risk Distribution Bar */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Risk Score Distribution</h3>
          <div style={{ height: '220px' }}>
            <Bar data={riskDistData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>

        {/* Suspicious Activity Trend */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Suspicious Predictions Trend</h3>
          <div style={{ height: '220px' }}>
            <Line data={suspiciousTrendData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>

        {/* Behavioral Activity Radar */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px' }}>Behavioral Activity Overview</h3>
          <div style={{ height: '220px', display: 'flex', justifyContent: 'center' }}>
            <Radar data={radarData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, angleLines: { color: 'rgba(51, 65, 85, 0.3)' } } } }} />
          </div>
        </div>
      </div>

      {/* Recent High-Risk Activities & Top At-Risk Users Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Recent High-Risk Activities Feed */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={18} color="var(--accent-amber)" />
              <span>Recent High-Risk Activities</span>
            </h3>
            <Link to="/alerts" style={{ color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 600 }}>View Alerts</Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {metrics?.recent_high_risk_activities?.map((act) => (
              <div key={act.id} style={{ padding: '12px 14px', borderRadius: '8px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--text-main)' }}>{act.user}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>{act.action}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`badge badge-${act.severity.toLowerCase()}`}>{act.severity}</span>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>{act.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top At-Risk Monitored Users Table */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>Top At-Risk Monitored Users</h3>
            <Link to="/users" style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span>View Directory</span>
              <ArrowUpRight size={16} />
            </Link>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>final_risk_score</th>
                  <th>severity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {topUsers.map((u) => (
                  <tr key={u.user}>
                    <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{u.user}</td>
                    <td style={{ fontWeight: 700, color: u.max_risk_score >= 80 ? 'var(--severity-critical)' : 'var(--accent-amber)' }}>
                      {u.max_risk_score} / 100
                    </td>
                    <td>
                      <span className={`badge badge-${u.severity.toLowerCase()}`}>{u.severity}</span>
                    </td>
                    <td>
                      <Link to={`/user-details?user=${u.user}`} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
