import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { usersAPI } from '../services/api';
import { Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, Eye, ShieldAlert, UserCheck } from 'lucide-react';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [searchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [severityFilter, setSeverityFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [sortBy, setSortBy] = useState('display_risk_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const responseData = await usersAPI.getMonitoredUsers({ search, severity: severityFilter });
      const userList = Array.isArray(responseData)
        ? responseData
        : (responseData?.users || responseData?.data || []);
      setUsers(userList);
    } catch (err) {
      console.error("Fetch users error:", err);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [severityFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchUsers();
  };

  // Sort and filter processing
  let processedUsers = users.filter((u) => {
    let match = true;
    const userIdStr = String(u.user || u.username || u.id || '');
    if (search.trim()) {
      const q = search.toLowerCase();
      match = match && (userIdStr.toLowerCase().includes(q) || String(u.status || '').toLowerCase().includes(q));
    }
    const score = u.display_risk_score ?? u.risk_score ?? u.max_risk_score ?? 0;
    if (riskFilter === 'high') {
      match = match && score >= 75;
    } else if (riskFilter === 'medium') {
      match = match && (score >= 45 && score < 75);
    } else if (riskFilter === 'low') {
      match = match && score < 45;
    }
    return match;
  });

  processedUsers.sort((a, b) => {
    const valA = a[sortBy] ?? (a.display_risk_score ?? a.risk_score ?? a.max_risk_score ?? 0);
    const valB = b[sortBy] ?? (b.display_risk_score ?? b.risk_score ?? b.max_risk_score ?? 0);
    if (typeof valA === 'string') {
      return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return sortOrder === 'asc' ? valA - valB : valB - valA;
  });

  const totalPages = Math.ceil(processedUsers.length / itemsPerPage) || 1;
  const currentUsers = processedUsers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>Monitored User Directory</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Real-time enterprise user monitoring table with ML risk probabilities, behavioral indicators, and severity scoring
        </p>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="glass-card" style={{ padding: '20px', marginBottom: '24px', display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
        <form onSubmit={handleSearchSubmit} style={{ flex: 1, display: 'flex', gap: '10px', minWidth: '280px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
            <input
              type="text"
              className="input-field"
              placeholder="Search by User ID (e.g. USR0157, DLM0051)..."
              style={{ paddingLeft: '40px' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary">Search</button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Filter size={16} color="var(--text-muted)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Severity:</span>
            <select 
              className="input-field" 
              style={{ width: '140px', padding: '6px 10px', fontSize: '0.8rem' }}
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); setCurrentPage(1); }}
            >
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Risk Range:</span>
            <select 
              className="input-field" 
              style={{ width: '140px', padding: '6px 10px', fontSize: '0.8rem' }}
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setCurrentPage(1); }}
            >
              <option value="">All Scores</option>
              <option value="high">High Risk (≥75)</option>
              <option value="medium">Medium (45-74)</option>
              <option value="low">Low Risk (&lt;45)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Directory Table */}
      <div className="glass-card" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading Monitored Users...</div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table className="custom-table">
                <thead>
                  <tr>
                    <th onClick={() => toggleSort('user')} style={{ cursor: 'pointer' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span>User</span>
                        <ArrowUpDown size={14} />
                      </div>
                    </th>
                    <th onClick={() => toggleSort('ml_risk_score')} style={{ cursor: 'pointer' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span>ML Risk Score</span>
                        <ArrowUpDown size={14} />
                      </div>
                    </th>
                    <th>ML Probability</th>
                    <th onClick={() => toggleSort('display_risk_score')} style={{ cursor: 'pointer' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span>Final Risk Score</span>
                        <ArrowUpDown size={14} />
                      </div>
                    </th>
                    <th>Severity</th>
                    <th>Prediction</th>
                    <th>Last Activity</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {currentUsers.map((u) => {
                    const userId = u.user || u.username || u.id;
                    const finalRiskScore = u.display_risk_score ?? u.risk_score ?? u.max_risk_score ?? 0;
                    const mlRiskScore = u.ml_risk_score ?? finalRiskScore;
                    const mlProbPercent = (
                      (u.prediction_probability ?? u.ml_probability ?? 0) * 100
                    ).toFixed(1);
                    const isSuspicious = u.prediction !== undefined ? u.prediction === 1 : finalRiskScore >= 50;
                    const predictionLabel = isSuspicious ? 'Suspicious (1)' : 'Normal (0)';
                    const predictionColor = isSuspicious ? 'var(--severity-critical)' : 'var(--severity-low)';
                    const severityLabel = u.severity || u.latest_severity || 'Low';

                    return (
                      <tr key={userId}>
                        <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{userId}</td>
                        <td style={{ fontWeight: 600 }}>{mlRiskScore} / 100</td>
                        <td style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{mlProbPercent}%</td>
                        <td style={{ fontWeight: 800, color: finalRiskScore >= 80 ? 'var(--severity-critical)' : finalRiskScore >= 70 ? 'var(--severity-high)' : finalRiskScore >= 50 ? 'var(--severity-medium)' : 'var(--severity-low)' }}>
                          {finalRiskScore} / 100
                        </td>
                        <td>
                          <span className={`badge badge-${severityLabel.toLowerCase()}`}>{severityLabel}</span>
                        </td>
                        <td style={{ fontWeight: 700, color: predictionColor }}>{predictionLabel}</td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.last_activity || '2010-01-04'}</td>

                        <td>
                          <span style={{
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            backgroundColor: u.status === 'Under Investigation' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                            color: u.status === 'Under Investigation' ? 'var(--severity-critical)' : 'var(--severity-low)'
                          }}>
                            {u.status || 'Active'}
                          </span>
                        </td>
                        <td>
                          <button 
                            onClick={() => navigate(`/user-details?user=${userId}`)} 
                            className="btn-secondary" 
                            style={{ padding: '6px 12px', fontSize: '0.75rem', gap: '6px' }}
                          >
                            <Eye size={14} />
                            <span>View Details</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing <strong>{currentUsers.length}</strong> of <strong>{processedUsers.length}</strong> monitored personnel
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  className="btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  <ChevronLeft size={16} />
                  <span>Previous</span>
                </button>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: 600, padding: '0 8px' }}>
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  className="btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  <span>Next</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Users;
