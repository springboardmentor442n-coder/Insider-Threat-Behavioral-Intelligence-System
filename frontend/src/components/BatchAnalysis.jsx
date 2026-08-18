import { useState, useMemo } from 'react';
import { predictBatch } from '../services/api';
import {
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

function BatchAnalysis() {
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError("Please select a valid CSV file.");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("No file selected.");
      return;
    }
    
    setIsAnalyzing(true);
    setError(null);
    setResults(null);
    setSummary(null);

    try {
      const data = await predictBatch(file);
      setResults(data.results);
      setSummary(data.summary);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze the batch file. Ensure all required columns are present.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadCSV = () => {
    if (!results) return;

    // Define columns
    const headers = [
      "Employee ID",
      "Device Connections",
      "Emails Sent",
      "Files Accessed",
      "Websites Visited",
      "Logon Count",
      "O", "C", "E", "A", "N",
      "Prediction",
      "Risk Level"
    ];

    // Build CSV string
    const csvRows = [];
    csvRows.push(headers.join(','));

    results.forEach(row => {
      const values = [
        row.employeeId,
        row.features.device_connections,
        row.features.emails_sent,
        row.features.files_accessed,
        row.features.websites_visited,
        row.features.logon_count,
        row.features.O,
        row.features.C,
        row.features.E,
        row.features.A,
        row.features.N,
        row.prediction,
        row.riskLevel
      ];
      csvRows.push(values.join(','));
    });

    const csvContent = "data:text/csv;charset=utf-8," + csvRows.join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `batch_analysis_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const chartData = useMemo(() => {
    if (!results || results.length === 0) return null;

    let normalCount = 0;
    let anomalyCount = 0;
    const riskCounts = {};
    
    let totalDeviceConnections = 0;
    let totalEmailsSent = 0;
    let totalFilesAccessed = 0;
    let totalWebsitesVisited = 0;
    let totalLogonCount = 0;

    const anomalies = [];

    results.forEach(row => {
      if (row.prediction === 'ANOMALY') {
        anomalyCount++;
        anomalies.push(row);
      } else {
        normalCount++;
      }

      const risk = row.riskLevel || 'UNKNOWN';
      riskCounts[risk] = (riskCounts[risk] || 0) + 1;

      totalDeviceConnections += row.features.device_connections || 0;
      totalEmailsSent += row.features.emails_sent || 0;
      totalFilesAccessed += row.features.files_accessed || 0;
      totalWebsitesVisited += row.features.websites_visited || 0;
      totalLogonCount += row.features.logon_count || 0;
    });

    const total = results.length;
    const anomalyPercentage = ((anomalyCount / total) * 100).toFixed(1);

    const predictionData = [
      { name: 'NORMAL', value: normalCount },
      { name: 'ANOMALY', value: anomalyCount }
    ];

    const riskData = Object.keys(riskCounts).map(key => ({
      name: key,
      value: riskCounts[key]
    }));

    const activityData = [
      { name: 'Dev Conn', value: parseFloat((totalDeviceConnections / total).toFixed(2)) },
      { name: 'Emails', value: parseFloat((totalEmailsSent / total).toFixed(2)) },
      { name: 'Files', value: parseFloat((totalFilesAccessed / total).toFixed(2)) },
      { name: 'Websites', value: parseFloat((totalWebsitesVisited / total).toFixed(2)) },
      { name: 'Logons', value: parseFloat((totalLogonCount / total).toFixed(2)) }
    ];

    return {
      predictionData,
      riskData,
      activityData,
      anomalies,
      total,
      normalCount,
      anomalyCount,
      anomalyPercentage
    };
  }, [results]);

  const RISK_COLORS = {
    'LOW': '#10b981',
    'MEDIUM': '#f59e0b',
    'HIGH': '#ef4444',
    'UNKNOWN': '#6b7280'
  };

  return (
    <div className="batch-analysis-container">
      <div className="page-header">
        <div className="header-title-row">
          <h1>Batch Analysis</h1>
        </div>
        <p className="page-subtitle">Upload a dataset for bulk behavioral prediction</p>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-header">
          <h2>Upload Dataset</h2>
        </div>
        <div style={{ padding: '1.5rem' }}>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
            Upload a CSV containing the following columns: user, device_connections, emails_sent, files_accessed, websites_visited, logon_count, O, C, E, A, N.
          </p>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <input 
              type="file" 
              accept=".csv"
              onChange={handleFileChange}
              style={{
                padding: '0.5rem',
                border: '1px dashed var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                background: 'var(--bg-secondary)',
                flex: 1,
                maxWidth: '400px'
              }}
            />
            <button 
              className="table-action-btn"
              onClick={handleUpload}
              disabled={!file || isAnalyzing}
              style={{ padding: '0.6rem 1.5rem', background: 'var(--accent-primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: (file && !isAnalyzing) ? 'pointer' : 'not-allowed', opacity: (file && !isAnalyzing) ? 1 : 0.6 }}
            >
              {isAnalyzing ? "Analyzing..." : "Run Batch Analysis"}
            </button>
          </div>
          {error && <div style={{ color: 'var(--accent-warning)', marginTop: '1rem', fontSize: '0.9rem' }}>{error}</div>}
        </div>
      </div>

      {summary && (
        <div className="summary-cards" style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <div className="card" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>TOTAL ANALYZED</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{summary.total}</div>
          </div>
          <div className="card" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>NORMAL BEHAVIOR</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent-success, #10b981)' }}>{summary.normal}</div>
          </div>
          <div className="card" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>ANOMALIES DETECTED</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent-warning, #f59e0b)' }}>{summary.anomaly}</div>
          </div>
        </div>
      )}

      {chartData && (
        <div className="visualizations-container" style={{ marginBottom: '2rem' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            {/* Prediction Distribution Chart */}
            <div className="card" style={{ padding: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Prediction Distribution</h3>
              <div style={{ height: '250px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={chartData.predictionData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      <Cell fill="#10b981" />
                      <Cell fill="#f59e0b" />
                    </Pie>
                    <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '4px' }} itemStyle={{ color: 'var(--text-primary)' }} />
                    <Legend wrapperStyle={{ color: 'var(--text-primary)' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Level Distribution Chart */}
            <div className="card" style={{ padding: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Risk Level Distribution</h3>
              <div style={{ height: '250px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData.riskData} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} allowDecimals={false} />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '4px' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {chartData.riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            {/* Anomaly Percentage */}
            <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
               <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem', alignSelf: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', width: '100%' }}>Anomaly Analysis</h3>
               <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
                 <div style={{ fontSize: '3.5rem', fontWeight: 'bold', color: chartData.anomalyCount > 0 ? 'var(--accent-warning)' : 'var(--accent-success)', lineHeight: 1 }}>
                   {chartData.anomalyPercentage}%
                 </div>
                 <div style={{ color: 'var(--text-secondary)', marginTop: '1rem', textAlign: 'center', fontSize: '0.95rem' }}>
                   {chartData.anomalyCount === 0 ? (
                     <span>No anomalies detected in this batch.</span>
                   ) : (
                     <span><strong>{chartData.anomalyCount}</strong> anomalies out of <strong>{chartData.total}</strong> records.</span>
                   )}
                 </div>
               </div>
            </div>

            {/* Feature Activity Summary */}
            <div className="card" style={{ padding: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Average Activity Metrics</h3>
              <div style={{ height: '200px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData.activityData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={true} vertical={false} />
                    <XAxis type="number" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" tick={{fontSize: 12}} width={70} />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '4px' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Anomaly Employees List */}
          <div className="card" style={{ padding: '0' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
              <h3 style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Anomaly Employees {chartData.anomalyCount > 0 ? `(${chartData.anomalyCount})` : ''}
              </h3>
            </div>
            {chartData.anomalyCount === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                No anomalous employees detected in this batch.
              </div>
            ) : (
              <div className="table-responsive" style={{ maxHeight: '250px', overflowY: 'auto', padding: '0 1rem 1rem 1rem' }}>
                <table className="data-table" style={{ marginTop: '1rem' }}>
                  <thead>
                    <tr>
                      <th>Employee ID</th>
                      <th>Prediction</th>
                      <th>Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.anomalies.map((emp, idx) => (
                      <tr key={idx}>
                        <td className="mono-cell" style={{ fontWeight: 'bold' }}>{emp.employeeId}</td>
                        <td style={{ color: 'var(--accent-warning)', fontWeight: 'bold' }}>{emp.prediction}</td>
                        <td>
                          <span className={`status-pill ${emp.riskLevel === 'HIGH' ? 'danger' : 'normal'}`}>{emp.riskLevel}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      )}

      {results && (
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>Analysis Results</h2>
            <button 
              onClick={downloadCSV}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                padding: '0.4rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Download CSV Report
            </button>
          </div>
          <div className="table-responsive" style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Activity Metrics (Dev/Email/File/Web/Log)</th>
                  <th>Psychometric (O/C/E/A/N)</th>
                  <th>Prediction</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {results.map((row, idx) => (
                  <tr key={idx}>
                    <td className="mono-cell" style={{ fontWeight: 'bold' }}>{row.employeeId}</td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {row.features.device_connections} / {row.features.emails_sent} / {row.features.files_accessed} / {row.features.websites_visited} / {row.features.logon_count}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {row.features.O} / {row.features.C} / {row.features.E} / {row.features.A} / {row.features.N}
                    </td>
                    <td>
                      <span style={{ fontWeight: 'bold', color: row.prediction === 'ANOMALY' ? 'var(--accent-warning)' : 'var(--accent-success)' }}>
                        {row.prediction}
                      </span>
                    </td>
                    <td>
                      <span className={`status-pill ${row.riskLevel === 'HIGH' ? 'danger' : 'normal'}`}>
                        {row.riskLevel}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default BatchAnalysis;
