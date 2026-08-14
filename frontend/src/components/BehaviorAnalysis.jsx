import { useState } from "react";
import PredictionForm from "./PredictionForm";
import ResultCard from "./ResultCard";

function BehaviorAnalysis({ recentAnalyses = [], setRecentAnalyses, selectedEmployee, setSelectedEmployee }) {
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const addRecentAnalysis = (analysis) => {
    if (setRecentAnalyses) {
      setRecentAnalyses((prev) => [analysis, ...prev]);
    }
  };

  return (
    <div className="behavior-analysis-container">
      <div className="page-header">
        <div className="header-title-row">
          <h1>Behavior Analysis</h1>
          <div className="live-indicator">
            <span className="status-dot pulsing"></span> BEHAVIORAL ANALYSIS
          </div>
        </div>
        <p className="page-subtitle">Evaluate employee activity patterns using behavioral intelligence models.</p>
      </div>

      <div className="analysis-workflow">
        <div className="workflow-step">EMPLOYEE ACTIVITY</div>
        <div className="workflow-arrow">→</div>
        <div className="workflow-step">BEHAVIORAL FEATURES</div>
        <div className="workflow-arrow">→</div>
        <div className="workflow-step">ANOMALY DETECTION</div>
        <div className="workflow-arrow">→</div>
        <div className="workflow-step">RISK ASSESSMENT</div>
      </div>
      
      <div className="dashboard-grid-ba">
        <div className="analysis-left-col">
          <div className="card">
            <h2 className="card-header">Activity Input</h2>
              <PredictionForm 
                setPredictionResult={setPredictionResult} 
                setIsLoading={setIsLoading} 
                isLoading={isLoading}
                addRecentAnalysis={addRecentAnalysis}
              />
          </div>
        </div>
        
        <div className="analysis-right-col">
          <div className="card result-panel-card">
            <h2 className="card-header">Analysis Result</h2>
            <ResultCard 
              result={predictionResult} 
              isLoading={isLoading} 
            />
          </div>

          <div className="card">
            <h2 className="card-header">Model Intelligence</h2>
            <div className="model-info-content">
              <div className="model-info-item">
                <span className="info-label">Primary Model</span>
                <span className="info-value">Isolation Forest</span>
              </div>
              <div className="model-info-item">
                <span className="info-label">Secondary Evaluated Model</span>
                <span className="info-value">Local Outlier Factor</span>
              </div>
              <p className="model-info-desc">
                Behavioral activity features are evaluated to identify anomalous patterns associated with potential insider-threat activity.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card recent-analysis-card">
        <h2 className="card-header">Recent Analysis (Session)</h2>
        <div className="recent-analysis-list">
          {recentAnalyses.length === 0 ? (
            <div className="empty-state">No analyses performed in this session.</div>
          ) : (
            <div className="recent-list-container">
              {recentAnalyses.map((item, index) => (
                <div key={index} className="recent-list-item">
                  <span className="recent-time">{item.timestamp}</span>
                  <span className="recent-id">ID: {item.employeeId}</span>
                  <span className={`recent-result ${item.prediction === "INSIDER" || item.prediction === "Threat" ? 'threat-text' : 'normal-text'}`}>
                    {item.prediction}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default BehaviorAnalysis;
