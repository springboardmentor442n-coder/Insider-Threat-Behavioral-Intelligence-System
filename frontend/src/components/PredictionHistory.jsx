function PredictionHistory({ recentAnalyses = [], setRecentAnalyses }) {
  const handleClearHistory = () => {
    if (window.confirm("Are you sure you want to clear your prediction history? This will not affect the backend model or datasets.")) {
      const user = sessionStorage.getItem("insightguard_user") || "default";
      setRecentAnalyses([]);
      localStorage.removeItem(`insightguard_data_${user}`);
    }
  };

  return (
    <div className="prediction-history-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="header-title-row">
            <h1>Prediction History</h1>
          </div>
          <p className="page-subtitle">Historical log of behavioral analyses conducted during the current session</p>
        </div>
        {recentAnalyses.length > 0 && (
          <button className="table-action-btn" onClick={handleClearHistory} style={{ borderColor: 'var(--accent-warning)', color: 'var(--accent-warning)' }}>
            Clear Prediction History
          </button>
        )}
      </div>

      <div className="card">
        <h2 className="card-header">Session Predictions</h2>
        
        {recentAnalyses.length === 0 ? (
          <div className="empty-state">No predictions yet. Run a Behavioral Analysis to generate your first prediction.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table" style={{ minWidth: '900px' }}>
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Employee</th>
                  <th>Prediction</th>
                  <th>Risk Level</th>
                  <th>Device Connections</th>
                  <th>Emails Sent</th>
                  <th>Files Accessed</th>
                  <th>Websites Visited</th>
                  <th>Logon Count</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((item, index) => {
                  const isThreat = item.prediction === "ANOMALY" || item.riskLevel === "HIGH";
                  return (
                    <tr key={index}>
                      <td className="muted-cell">{item.timestamp}</td>
                      <td className="emp-name" style={{ fontSize: '0.85rem' }}>{item.employeeId || 'Unknown'}</td>
                      <td style={{ fontWeight: 600 }}>{item.prediction}</td>
                      <td>
                        <span className={`status-pill ${isThreat ? 'danger' : 'normal'}`}>
                          {item.riskLevel || (isThreat ? 'HIGH' : 'LOW')}
                        </span>
                      </td>
                      <td className="mono-cell">{item.activity?.deviceConnections ?? 'N/A'}</td>
                      <td className="mono-cell">{item.activity?.emailsSent ?? 'N/A'}</td>
                      <td className="mono-cell">{item.activity?.filesAccessed ?? 'N/A'}</td>
                      <td className="mono-cell">{item.activity?.websitesVisited ?? 'N/A'}</td>
                      <td className="mono-cell">{item.activity?.logonCount ?? 'N/A'}</td>
                      <td>
                        <span className="status-pill success">{item.status || "COMPLETED"}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default PredictionHistory;
