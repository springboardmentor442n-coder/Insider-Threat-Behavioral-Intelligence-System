import { useState, useMemo } from 'react';
import allEmployees from '../employees.json';

function Employees({ setCurrentRoute, recentAnalyses = [], setSelectedEmployee }) {
  const [searchQuery, setSearchQuery] = useState('');

  const directoryData = allEmployees;

  const filteredEmployees = useMemo(() => {
    if (!searchQuery) return directoryData;
    const lowerQuery = searchQuery.toLowerCase();
    return directoryData.filter(emp => emp.id.toLowerCase().includes(lowerQuery));
  }, [searchQuery, directoryData]);

  const handleAnalyzeClick = (empId) => {
    if (setSelectedEmployee) {
      setSelectedEmployee(empId);
    }
    setCurrentRoute('BehaviorAnalysis');
  };

  return (
    <div className="employees-container">
      <div className="page-header">
        <div className="header-title-row">
          <h1>Employees</h1>
        </div>
        <p className="page-subtitle">Directory of monitored personnel and behavioral summaries</p>
      </div>

      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>Monitored Personnel</h2>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Total Employees: {directoryData.length}</span>
        </div>
        
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <input
            type="text"
            placeholder="Search employee by ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              maxWidth: '400px',
              padding: '0.5rem 1rem',
              background: 'var(--bg-main)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-sm)',
              outline: 'none'
            }}
          />
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Activity Status</th>
                <th>ML Risk Status</th>
                <th>Last Analysis</th>
                <th className="action-column">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.map((emp, index) => {
                // Find if this employee was analyzed in the current session
                const analysis = recentAnalyses.find(a => a.employeeId === emp.id);
                const riskStatus = analysis ? analysis.riskLevel : "UNANALYZED";
                const lastAnalysis = analysis ? analysis.timestamp : "N/A";
                const isAnalyzed = !!analysis;

                return (
                  <tr key={index}>
                    <td className="mono-cell" style={{ fontWeight: 'bold' }}>{emp.id}</td>
                    <td>
                      <span className="status-pill info">Unknown</span>
                    </td>
                    <td>
                      <span className={`status-pill ${isAnalyzed ? (riskStatus === 'HIGH' ? 'danger' : 'normal') : 'info'}`}>
                        {riskStatus}
                      </span>
                    </td>
                    <td className="muted-cell">{lastAnalysis}</td>
                    <td className="action-column">
                      <button className="table-action-btn" onClick={() => handleAnalyzeClick(emp.id)}>
                        Analyze
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Employees;
