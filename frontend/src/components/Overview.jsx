import allEmployees from '../employees.json';

function Overview({ setCurrentRoute, recentAnalyses = [] }) {
  return (
    <div className="overview-container">
      <div className="page-header">
        <div className="header-title-row">
          <h1>Security Overview</h1>
          <div className="live-indicator">
            <span className="status-dot pulsing"></span> SYSTEM OPERATIONAL
          </div>
        </div>
        <p className="page-subtitle">Behavioral intelligence monitoring and anomaly detection workspace</p>
      </div>

      <div className="overview-grid-3col">
        {/* System Status Panel */}
        <div className="card">
          <h2 className="card-header">System Status</h2>
          <div className="status-panel-group">
            <div className="status-panel">
              <span className="status-panel-label">FRONTEND</span>
              <span className="status-panel-value">
                <span className="status-dot"></span> ONLINE
              </span>
            </div>
            <div className="status-panel">
              <span className="status-panel-label">BACKEND API</span>
              <span className="status-panel-value">
                <span className="status-dot"></span> CONNECTED
              </span>
            </div>
            <div className="status-panel">
              <span className="status-panel-label">ML MODEL</span>
              <span className="status-panel-value">
                <span className="status-dot"></span> READY
              </span>
            </div>
          </div>
        </div>

        {/* Model Intelligence Panel */}
        <div className="card" style={{ gridColumn: "span 2" }}>
          <h2 className="card-header">Model Intelligence</h2>
          <div className="overview-model-info">
            <div className="model-info-block">
              <span className="info-label">PRIMARY DEPLOYMENT MODEL</span>
              <span className="info-value">Isolation Forest</span>
            </div>
            <div className="model-info-block" style={{ marginTop: '1rem' }}>
              <span className="info-label">SECONDARY EVALUATED MODEL</span>
              <span className="info-value">Local Outlier Factor</span>
            </div>
            <p className="model-info-desc" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-light)', paddingTop: '1rem' }}>
              Isolation Forest is used for anomaly detection, while Local Outlier Factor was evaluated as an alternative anomaly detection approach.
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Pipeline */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-header">Analysis Pipeline</h2>
        <div className="pipeline-flow">
          <div className="pipeline-box">
            <div className="pipeline-box-title">Employee Activity</div>
            <div className="pipeline-box-desc">Behavioral activity records</div>
          </div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-box">
            <div className="pipeline-box-title">Behavioral Features</div>
            <div className="pipeline-box-desc">Construction of behavioral features</div>
          </div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-box">
            <div className="pipeline-box-title">ML Analysis</div>
            <div className="pipeline-box-desc">Prediction and evaluation</div>
          </div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-box">
            <div className="pipeline-box-title">Anomaly Detection</div>
            <div className="pipeline-box-desc">ML-based identification of unusual patterns</div>
          </div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-box">
            <div className="pipeline-box-title">Risk Assessment</div>
            <div className="pipeline-box-desc">Interpretation of prediction output</div>
          </div>
        </div>
      </div>

      <div className="overview-grid-2col">
        {/* Behavioral Data Sources */}
        <div className="card">
          <h2 className="card-header">Behavioral Data Sources</h2>
          <ul className="data-sources-list">
            <li>Device Activity</li>
            <li>Email Activity</li>
            <li>File Activity</li>
            <li>HTTP/Web Activity</li>
            <li>Logon Activity</li>
            <li>Psychometric/OCEAN Profile</li>
          </ul>
          <p className="data-sources-desc">
            These sources contribute behavioral information used during preprocessing and feature construction.
          </p>
        </div>

        {/* Feature Groups */}
        <div className="card">
          <h2 className="card-header">Behavioral Feature Groups</h2>
          <div className="feature-groups">
            <div className="feature-group-col">
              <h3 className="feature-group-title">ACTIVITY METRICS</h3>
              <ul>
                <li>Device Connections</li>
                <li>Emails Sent</li>
                <li>Files Accessed</li>
                <li>Websites Visited</li>
                <li>Logon Count</li>
              </ul>
            </div>
            <div className="feature-group-col">
              <h3 className="feature-group-title">PSYCHOMETRIC PROFILE</h3>
              <ul>
                <li>Openness</li>
                <li>Conscientiousness</li>
                <li>Extraversion</li>
                <li>Agreeableness</li>
                <li>Neuroticism</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="overview-grid-3col">
        {/* Quick Analysis */}
        <div className="card quick-analysis-card" style={{ gridColumn: "span 2", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <h2 className="card-header">Run Behavior Analysis</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Evaluate employee activity patterns using the project's anomaly detection pipeline.
          </p>
          <button className="submit-btn" style={{ alignSelf: "flex-start", width: "auto" }} onClick={() => setCurrentRoute('BehaviorAnalysis')}>
            OPEN BEHAVIOR ANALYSIS →
          </button>
        </div>

        {/* Analysis Summary & About */}
        <div className="right-col-stack">
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h2 className="card-header">Analysis Summary</h2>
            {recentAnalyses.length > 0 ? (
              <div className="status-panel-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Last Employee Analyzed</span>
                  <span className="status-panel-value" style={{ fontWeight: 'bold' }}>{recentAnalyses[0].employeeId || 'Unknown'}</span>
                </div>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Last Prediction</span>
                  <span className="status-panel-value" style={{ fontWeight: 'bold' }}>{recentAnalyses[0].prediction}</span>
                </div>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Last Risk Level</span>
                  <span className={`status-panel-value ${recentAnalyses[0].prediction === "INSIDER" || recentAnalyses[0].prediction === "Threat" ? 'threat-text' : 'normal-text'}`}>
                    {recentAnalyses[0].prediction === "INSIDER" || recentAnalyses[0].prediction === "Threat" ? 'HIGH' : 'LOW'}
                  </span>
                </div>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Total Employees</span>
                  <span className="status-panel-value" style={{ color: 'var(--accent-secondary)' }}>{allEmployees.length}</span>
                </div>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Total Analyses</span>
                  <span className="status-panel-value" style={{ color: 'var(--accent-secondary)' }}>{recentAnalyses.length}</span>
                </div>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Employees Analyzed</span>
                  <span className="status-panel-value" style={{ color: 'var(--accent-secondary)' }}>
                    {new Set(recentAnalyses.map(a => a.employeeId)).size}
                  </span>
                </div>
              </div>
            ) : (
              <div className="status-panel-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div className="status-panel" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <span className="status-panel-label">Total Employees</span>
                  <span className="status-panel-value" style={{ color: 'var(--accent-secondary)' }}>{allEmployees.length}</span>
                </div>
                <div style={{ color: "var(--text-muted)", fontSize: '0.9rem', padding: '0.5rem 0' }}>
                  Awaiting first analysis
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="card-header">About InsightGuard</h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", margin: 0, lineHeight: 1.6 }}>
              INSIGHTGUARD is a Behavioral Intelligence system designed to analyze employee activity patterns and identify anomalous behavior that may indicate potential insider-threat activity.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}

export default Overview;

