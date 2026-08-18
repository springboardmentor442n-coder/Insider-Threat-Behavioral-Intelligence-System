import { useState, useMemo, useEffect } from 'react';
import { getEmployeeAnalysis } from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip, Cell
} from 'recharts';

function Employees({ setCurrentRoute, recentAnalyses = [], setRecentAnalyses, setSelectedEmployee }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [directoryData, setDirectoryData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/employees")
      .then(res => res.json())
      .then(data => {
        const mappedData = data.employees.map(id => ({ id }));
        setDirectoryData(mappedData);
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Failed to load employees:", err);
        setIsLoading(false);
      });
  }, []);

  const filteredEmployees = useMemo(() => {
    if (!searchQuery) return directoryData;
    const lowerQuery = searchQuery.toLowerCase();
    return directoryData.filter(emp => emp.id.toLowerCase().includes(lowerQuery));
  }, [searchQuery, directoryData]);

  const handleAnalyzeClick = async (empId) => {
    setIsAnalyzing(true);
    try {
      const data = await getEmployeeAnalysis(empId);

      const riskLevel = data.prediction === "ANOMALY" || data.prediction === "INSIDER" ? "HIGH" : "LOW";

      // Update global history
      if (setRecentAnalyses) {
        setRecentAnalyses(prev => {
          const newAnalysis = {
            id: Math.random().toString(36).substring(7).toUpperCase(),
            employeeId: empId,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            prediction: data.prediction,
            riskLevel: riskLevel,
            activity: {
              deviceConnections: data.features.device_connections,
              emailsSent: data.features.emails_sent,
              filesAccessed: data.features.files_accessed,
              websitesVisited: data.features.websites_visited,
              logonCount: data.features.logon_count
            },
            ocean: {
              openness: data.features.O,
              conscientiousness: data.features.C,
              extraversion: data.features.E,
              agreeableness: data.features.A,
              neuroticism: data.features.N
            },
            status: "COMPLETED",
            source: "MANUAL"
          };
          return [newAnalysis, ...prev];
        });
      }

      setSelectedAnalysis(data);
    } catch (err) {
      console.error("Failed to analyze employee:", err);
      alert("Failed to analyze employee. See console for details.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadAnalysisCSV = () => {
    if (!selectedAnalysis) return;
    
    const headers = [
      "Employee ID",
      "Device Connections",
      "Emails Sent",
      "Files Accessed",
      "Websites Visited",
      "Logon Count",
      "O", "C", "E", "A", "N",
      "Prediction",
      "Risk Level",
      "Timestamp"
    ];
    
    const riskLevel = selectedAnalysis.prediction === "ANOMALY" || selectedAnalysis.prediction === "INSIDER" ? "HIGH" : "LOW";
    
    const values = [
      selectedAnalysis.employeeId,
      selectedAnalysis.features.device_connections,
      selectedAnalysis.features.emails_sent,
      selectedAnalysis.features.files_accessed,
      selectedAnalysis.features.websites_visited,
      selectedAnalysis.features.logon_count,
      selectedAnalysis.features.O,
      selectedAnalysis.features.C,
      selectedAnalysis.features.E,
      selectedAnalysis.features.A,
      selectedAnalysis.features.N,
      selectedAnalysis.prediction,
      riskLevel,
      selectedAnalysis.timestamp
    ];
    
    const csvContent = "data:text/csv;charset=utf-8," + headers.join(',') + '\n' + values.join(',');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `employee_analysis_${selectedAnalysis.employeeId}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  let behavioralData = [];
  let psychometricData = [];
  
  if (selectedAnalysis) {
    behavioralData = [
      { name: 'Dev Conn', value: selectedAnalysis.features.device_connections },
      { name: 'Emails', value: selectedAnalysis.features.emails_sent },
      { name: 'Files', value: selectedAnalysis.features.files_accessed },
      { name: 'Websites', value: selectedAnalysis.features.websites_visited },
      { name: 'Logons', value: selectedAnalysis.features.logon_count }
    ];
    
    psychometricData = [
      { name: 'O', full: 'Openness', value: selectedAnalysis.features.O },
      { name: 'C', full: 'Conscientiousness', value: selectedAnalysis.features.C },
      { name: 'E', full: 'Extraversion', value: selectedAnalysis.features.E },
      { name: 'A', full: 'Agreeableness', value: selectedAnalysis.features.A },
      { name: 'N', full: 'Neuroticism', value: selectedAnalysis.features.N }
    ];
  }

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
                      <button className="table-action-btn" onClick={() => handleAnalyzeClick(emp.id)} disabled={isAnalyzing}>
                        {isAnalyzing ? "..." : "Analyze"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Side Panel Overlay */}
      {selectedAnalysis && (
        <div className="side-panel-overlay" onClick={() => setSelectedAnalysis(null)} style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', justifyContent: 'flex-end'
        }}>
          <div className="side-panel" onClick={(e) => e.stopPropagation()} style={{
            width: '500px', backgroundColor: 'var(--bg-main)', height: '100%', borderLeft: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', overflowY: 'auto', boxShadow: '-4px 0 15px rgba(0,0,0,0.1)'
          }}>
            <div className="side-panel-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>INDIVIDUAL ANALYSIS REPORT</h2>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.25rem' }}>{selectedAnalysis.employeeId}</div>
              </div>
              <button onClick={() => setSelectedAnalysis(null)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.5rem' }}>&times;</button>
            </div>

            <div className="side-panel-content" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>MODEL PREDICTION</div>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem', color: selectedAnalysis.prediction === "ANOMALY" ? 'var(--accent-warning, #f59e0b)' : 'var(--accent-success, #10b981)' }}>
                    {selectedAnalysis.prediction}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>RISK LEVEL</div>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem', color: selectedAnalysis.prediction === "ANOMALY" ? 'var(--accent-warning, #f59e0b)' : 'var(--accent-success, #10b981)' }}>
                    {selectedAnalysis.prediction === "ANOMALY" ? "HIGH" : "LOW"}
                  </div>
                </div>
              </div>

              <div>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', fontWeight: 600 }}>
                  Behavioral Activity Metrics
                </div>
                <div style={{ height: '220px', width: '100%', background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={behavioralData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 11}} angle={-45} textAnchor="end" />
                      <YAxis stroke="var(--text-secondary)" tick={{fontSize: 11}} />
                      <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '4px' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                      <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', fontWeight: 600 }}>
                  Psychometric Profile (OCEAN)
                </div>
                <div style={{ height: '200px', width: '100%', background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={psychometricData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={true} vertical={false} />
                      <XAxis type="number" stroke="var(--text-secondary)" tick={{fontSize: 11}} domain={[0, 10]} />
                      <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" tick={{fontSize: 11}} width={30} />
                      <RechartsTooltip 
                        contentStyle={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '4px' }} 
                        cursor={{fill: 'rgba(255,255,255,0.05)'}} 
                        formatter={(value, name, props) => [value, props.payload.full]}
                      />
                      <Bar dataKey="value" fill="#10b981" radius={[0, 4, 4, 0]} barSize={15}>
                        {psychometricData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={selectedAnalysis.prediction === 'ANOMALY' ? '#f59e0b' : '#10b981'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.5rem' }}>
                <button 
                  onClick={downloadAnalysisCSV}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--accent-primary)',
                    color: 'var(--accent-primary)',
                    padding: '0.6rem 1.2rem',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontWeight: 500,
                    width: '100%',
                    justifyContent: 'center',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'; }}
                  onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download Report (CSV)
                </button>
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                  Model: {selectedAnalysis.model}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  {new Date(selectedAnalysis.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Employees;
