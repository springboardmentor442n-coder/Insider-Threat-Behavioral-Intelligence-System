import React, { useState, useEffect } from 'react';
import { predictionAPI, usersAPI, analysisAPI } from '../services/api';
import { Cpu, Play, BarChart3, AlertCircle, CheckCircle2, Upload, FileText, FolderArchive, ShieldAlert, Download, AlertTriangle, ListFilter, UserSearch } from 'lucide-react';
import { Bar } from 'react-chartjs-2';
import { Link } from 'react-router-dom';

const ThreatDetection = () => {
  const [activeTab, setActiveTab] = useState('simulator'); // 'simulator' | 'bulk_analysis'

  const [monitoredUsers, setMonitoredUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [userLoading, setUserLoading] = useState(false);
  const [userError, setUserError] = useState(null);

  // Manual 19-feature simulator state in exact schema order expected by model
  const [features, setFeatures] = useState({
    logon_count: 2,
    logoff_count: 2,
    off_hours_logons: 3,
    unique_pcs: 2,
    device_connects: 4,
    device_disconnects: 4,
    unique_device_pcs: 1,
    file_activity_count: 15,
    unique_file_pcs: 1,
    unique_files: 10,
    sensitive_file_count: 8,
    email_count: 12,
    attachment_count: 5,
    total_email_size: 150000,
    unique_email_pcs: 1,
    external_email_count: 6,
    http_request_count: 80,
    unique_http_urls: 20,
    off_hours_http: 45
  });

  const [predictionResult, setPredictionResult] = useState(null);
  const [importanceData, setImportanceData] = useState([]);
  const [highRiskUsers, setHighRiskUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Bulk Analysis Upload State (Mode 1 & Mode 2)
  const [uploadMode, setUploadMode] = useState('mode1'); // 'mode1' | 'mode2'
  const [mode1File, setMode1File] = useState(null);
  const [certFiles, setCertFiles] = useState({ logon: null, device: null, file: null, email: null, http: null });
  const [bulkLoading, setBulkLoading] = useState(false);
  const [bulkResponse, setBulkResponse] = useState(null);
  const [bulkError, setBulkError] = useState(null);

  const extractArray = (res) => {
    if (Array.isArray(res)) return res;
    if (Array.isArray(res?.users)) return res.users;
    if (Array.isArray(res?.data)) return res.data;
    return [];
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [imp, usersRes, allUsersRes] = await Promise.all([
          predictionAPI.getFeatureImportance().catch(() => []),
          usersAPI.getMonitoredUsers({ minRisk: 60 }).catch(() => []),
          usersAPI.getMonitoredUsers({ limit: 100 }).catch(() => [])
        ]);
        const impArray = Array.isArray(imp) ? imp : [];
        const usersArray = extractArray(usersRes);
        const allUsersArray = extractArray(allUsersRes);

        setImportanceData(impArray);
        setHighRiskUsers(usersArray);
        setMonitoredUsers(allUsersArray);

        if (allUsersArray.length > 0 && allUsersArray[0]?.user) {
          handleSelectUser(allUsersArray[0].user, false);
        }
      } catch (err) {
        console.error("Threat detection fetch error:", err);
      }
    };
    fetchData();
  }, []);

  const runInferenceForFeatures = async (featureObj) => {
    setLoading(true);
    try {
      const res = await predictionAPI.predict(featureObj);
      setPredictionResult(res);
    } catch (err) {
      console.error("Prediction error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = async (userId, autoRun = false) => {
    if (!userId) return;
    setSelectedUser(userId);
    setUserLoading(true);
    setUserError(null);
    try {
      const userFeatData = await usersAPI.getUserFeatures(userId);
      if (userFeatData && userFeatData.features) {
        setFeatures(userFeatData.features);
        if (autoRun) {
          await runInferenceForFeatures(userFeatData.features);
        }
      }
    } catch (err) {
      console.error("Fetch user features error:", err);
      setUserError(`Could not load feature records for ${userId}`);
    } finally {
      setUserLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFeatures(prev => ({
      ...prev,
      [name]: value === '' ? '' : (parseFloat(value) || 0)
    }));
  };

  const handlePredict = async () => {
    const cleanFeatures = {};
    Object.keys(features).forEach(k => {
      const val = features[k];
      cleanFeatures[k] = val === '' ? 0 : (parseFloat(val) || 0);
    });
    await runInferenceForFeatures(cleanFeatures);
  };


  // Submit Bulk Analysis Upload
  const handleBulkSubmit = async (e) => {
    e.preventDefault();
    setBulkLoading(true);
    setBulkError(null);
    setBulkResponse(null);

    const formData = new FormData();

    if (uploadMode === 'mode1') {
      if (!mode1File) {
        setBulkError("Please select a 19-feature CSV file.");
        setBulkLoading(false);
        return;
      }
      formData.append('file', mode1File);
    } else {
      if (!certFiles.logon && !certFiles.device && !certFiles.file && !certFiles.email && !certFiles.http) {
        setBulkError("Please select at least one raw CERT log file (logon.csv, device.csv, file.csv, email.csv, http.csv).");
        setBulkLoading(false);
        return;
      }
      if (certFiles.logon) formData.append('logon_file', certFiles.logon);
      if (certFiles.device) formData.append('device_file', certFiles.device);
      if (certFiles.file) formData.append('file_file', certFiles.file);
      if (certFiles.email) formData.append('email_file', certFiles.email);
      if (certFiles.http) formData.append('http_file', certFiles.http);
    }

    try {
      const res = await analysisAPI.uploadAnalysis(formData);
      setBulkResponse(res);
    } catch (err) {
      setBulkError(err?.response?.data?.detail || "Failed to run bulk analysis upload.");
    } finally {
      setBulkLoading(false);
    }
  };

  const safeImportanceData = Array.isArray(importanceData) ? importanceData : [];
  const barChartData = {
    labels: safeImportanceData.map(i => i.feature),
    datasets: [
      {
        label: 'Gradient Boosting Feature Importance Weight',
        data: safeImportanceData.map(i => i.importance),
        backgroundColor: '#38bdf8',
        borderRadius: 4,
      },
    ],
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>ML Threat Inference & Data Upload Workspace</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Trained Gradient Boosting model inference engine & bulk dataset analysis system
        </p>
      </div>

      {/* Mode Navigation Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '28px' }}>
        <button
          onClick={() => setActiveTab('simulator')}
          className={activeTab === 'simulator' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '10px 18px', fontSize: '0.9rem' }}
        >
          <Cpu size={18} />
          <span>Real-time Feature Simulator</span>
        </button>

        <button
          onClick={() => setActiveTab('bulk_analysis')}
          className={activeTab === 'bulk_analysis' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '10px 18px', fontSize: '0.9rem' }}
        >
          <Upload size={18} />
          <span>Bulk CSV Data Analysis & Ingestion</span>
        </button>
      </div>

      {/* TAB 1: Real-time Feature Simulator */}
      {activeTab === 'simulator' && (
        <>
          {/* Dataset User Selector Bar for Rule 6 */}
          <div className="glass-card" style={{ padding: '18px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <UserSearch size={22} color="var(--accent-cyan)" />
              <div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>Dataset-Based Employee Analysis</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Select a real employee ID from dataset to auto-fill behavioral features & run model inference</div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <select
                className="input-field"
                style={{ width: '220px', padding: '8px 12px', fontSize: '0.85rem', fontWeight: 600 }}
                value={selectedUser}
                onChange={(e) => handleSelectUser(e.target.value, true)}
                disabled={userLoading}
              >
                <option value="">-- Select Monitored User --</option>
                {(Array.isArray(monitoredUsers) ? monitoredUsers : []).map((u) => (
                  <option key={u.user} value={u.user}>
                    {u.user} (Risk: {u.max_risk_score ?? u.risk_score ?? 0} / 100)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {userError && (
            <div style={{ padding: '12px 16px', background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--severity-critical)', borderRadius: '8px', marginBottom: '20px', fontSize: '0.85rem' }}>
              {userError}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Classification Output</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: predictionResult?.prediction === 1 ? 'var(--severity-critical)' : 'var(--severity-low)', marginTop: '4px' }}>
                {predictionResult ? (predictionResult.prediction === 1 ? 'SUSPICIOUS (1)' : 'NORMAL (0)') : '---'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>Trained Model Binary Prediction</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Prediction Probability</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '4px' }}>
                {predictionResult ? `${(predictionResult.prediction_probability * 100).toFixed(2)}%` : '0.00%'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>Model inference probability</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Behavioral Risk Score</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-purple)', marginTop: '4px' }}>
                {predictionResult ? `${predictionResult.behavioral_risk_score}` : '0'} <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>/ 100</span>
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>Rule calculation formula</div>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Final Risk Score</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: predictionResult?.final_risk_score >= 80 ? 'var(--severity-critical)' : 'var(--accent-purple)', marginTop: '4px' }}>
                {predictionResult ? predictionResult.final_risk_score : 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>/ 100</span>
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>0.7 * ML + 0.3 * Behavioral</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
            <div className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Cpu size={20} color="var(--accent-cyan)" />
                  <span>Behavioral Feature Inputs (19 Features)</span>
                </h3>
              </div>


              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', maxHeight: '460px', overflowY: 'auto', paddingRight: '6px' }}>
                {Object.keys(features).map((key) => (
                  <div key={key}>
                    <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '4px' }}>
                      {key}
                    </label>
                    <input
                      type="number"
                      name={key}
                      className="input-field"
                      value={features[key]}
                      onChange={handleChange}
                      style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                    />
                  </div>
                ))}
              </div>

              <button 
                onClick={handlePredict} 
                className="btn-primary"
                style={{ width: '100%', marginTop: '20px', justifyContent: 'center', padding: '12px' }}
                disabled={loading}
              >
                <Play size={18} />
                <span>{loading ? 'Evaluating Model...' : 'Run Risk Inference'}</span>
              </button>
            </div>

            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px' }}>Inference Prediction Output</h3>

                {predictionResult ? (
                  <div>
                    <div style={{
                      padding: '20px',
                      borderRadius: '12px',
                      backgroundColor: predictionResult.prediction === 1 ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                      border: predictionResult.prediction === 1 ? '1px solid rgba(244, 63, 94, 0.4)' : '1px solid rgba(16, 185, 129, 0.4)',
                      marginBottom: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px'
                    }}>
                      {predictionResult.prediction === 1 ? (
                        <AlertCircle size={44} color="var(--severity-critical)" />
                      ) : (
                        <CheckCircle2 size={44} color="var(--severity-low)" />
                      )}
                      <div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>ML Binary Classification</div>
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: predictionResult.prediction === 1 ? 'var(--severity-critical)' : 'var(--severity-low)' }}>
                          {predictionResult.prediction === 1 ? 'SUSPICIOUS INSIDER THREAT (1)' : 'NORMAL BEHAVIOR (0)'}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '20px' }}>
                      <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>prediction_probability</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                          {(predictionResult.prediction_probability * 100).toFixed(2)}%
                        </div>
                      </div>

                      <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>final_risk_score</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-purple)' }}>
                          {predictionResult.final_risk_score} / 100
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Severity Level</span>
                      <span className={`badge badge-${predictionResult.severity.toLowerCase()}`}>
                        {predictionResult.severity}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px' }}>Run inference to evaluate model response.</div>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* TAB 2: Bulk CSV Data Analysis Hub */}
      {activeTab === 'bulk_analysis' && (
        <div style={{ maxWidth: '960px', margin: '0 auto' }}>
          {/* Requirement 12: Help & Instruction Area */}
          <div className="glass-card" style={{ padding: '20px 24px', marginBottom: '20px', background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={18} />
              <span>CERT 4.2 Dataset Testing & Pipeline Guidelines</span>
            </h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
              <strong>Preferred Data Source:</strong> Use the official CERT Insider Threat Dataset r4.2.
              <br />
              • <strong>Mode 1 (Engineered CSV):</strong> Upload a 19-feature matrix CSV containing the exact schema: <code>logon_count</code>, <code>logoff_count</code>, <code>off_hours_logons</code>, <code>unique_pcs</code>, <code>device_connects</code>, <code>device_disconnects</code>, <code>unique_device_pcs</code>, <code>file_activity_count</code>, <code>unique_file_pcs</code>, <code>unique_files</code>, <code>sensitive_file_count</code>, <code>email_count</code>, <code>attachment_count</code>, <code>total_email_size</code>, <code>unique_email_pcs</code>, <code>external_email_count</code>, <code>http_request_count</code>, <code>unique_http_urls</code>, <code>off_hours_http</code>.
              <br />
              • <strong>Mode 2 (CERT Raw Activity Files):</strong> Upload raw CERT log CSVs (<code>logon.csv</code>, <code>device.csv</code>, <code>file.csv</code>, <code>email.csv</code>, <code>http.csv</code>). The backend pipeline automatically performs data cleaning, feature extraction, scaling, and Gradient Boosting ML inference.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '28px', marginBottom: '28px' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Upload size={22} color="var(--accent-cyan)" />
              <span>Bulk Analysis Engine</span>
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '20px' }}>
              Select dataset type below to run validation, scaler transform, and Gradient Boosting inference. Results are saved to SQLite database.
            </p>


            {/* Mode Switcher */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
              <button
                type="button"
                onClick={() => setUploadMode('mode1')}
                className={uploadMode === 'mode1' ? 'btn-primary' : 'btn-secondary'}
                style={{ padding: '8px 14px', fontSize: '0.85rem' }}
              >
                <FileText size={16} />
                <span>Mode 1: 19-Feature Engineered CSV</span>
              </button>

              <button
                type="button"
                onClick={() => setUploadMode('mode2')}
                className={uploadMode === 'mode2' ? 'btn-primary' : 'btn-secondary'}
                style={{ padding: '8px 14px', fontSize: '0.85rem' }}
              >
                <FolderArchive size={16} />
                <span>Mode 2: CERT Raw Activity CSVs</span>
              </button>
            </div>

            <form onSubmit={handleBulkSubmit}>
              {uploadMode === 'mode1' ? (
                <div style={{ border: '2px dashed var(--border-color)', borderRadius: '12px', padding: '36px', textAlign: 'center', background: 'var(--bg-secondary)', marginBottom: '20px' }}>
                  <Upload size={36} color="var(--accent-cyan)" style={{ marginBottom: '10px' }} />
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                    Select 19-Feature Dataset File (e.g. daily_behavioral_features.csv)
                  </div>
                  <input type="file" accept=".csv" onChange={(e) => setMode1File(e.target.files[0])} style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }} />
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>logon.csv</label>
                    <input type="file" accept=".csv" onChange={(e) => setCertFiles(f => ({ ...f, logon: e.target.files[0] }))} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} />
                  </div>

                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>device.csv</label>
                    <input type="file" accept=".csv" onChange={(e) => setCertFiles(f => ({ ...f, device: e.target.files[0] }))} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} />
                  </div>

                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>file.csv</label>
                    <input type="file" accept=".csv" onChange={(e) => setCertFiles(f => ({ ...f, file: e.target.files[0] }))} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} />
                  </div>

                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>email.csv</label>
                    <input type="file" accept=".csv" onChange={(e) => setCertFiles(f => ({ ...f, email: e.target.files[0] }))} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} />
                  </div>

                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>http.csv</label>
                    <input type="file" accept=".csv" onChange={(e) => setCertFiles(f => ({ ...f, http: e.target.files[0] }))} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} />
                  </div>
                </div>
              )}

              {bulkError && (
                <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.4)', color: 'var(--severity-critical)', fontSize: '0.85rem', marginBottom: '16px' }}>
                  {bulkError}
                </div>
              )}

              <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px' }} disabled={bulkLoading}>
                <Play size={18} />
                <span>{bulkLoading ? 'Executing Validation & ML Inference...' : 'Upload & Run Bulk Analysis'}</span>
              </button>
            </form>
          </div>

          {/* Bulk Analysis Response Cards & Detailed Table */}
          {bulkResponse && (
            <div>
              {/* Summary Stats Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '24px' }}>
                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Total Rows</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>{bulkResponse.total_rows}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{bulkResponse.successful_rows} Passed / {bulkResponse.failed_rows} Failed</div>
                </div>

                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Predictions</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '2px' }}>
                    Normal: {bulkResponse.normal_predictions}
                  </div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--severity-critical)' }}>
                    Suspicious: {bulkResponse.suspicious_predictions}
                  </div>
                </div>

                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Critical / High</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--severity-critical)', marginTop: '2px' }}>
                    {bulkResponse.critical_results + bulkResponse.high_results}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Critical: {bulkResponse.critical_results} | High: {bulkResponse.high_results}</div>
                </div>

                <div className="glass-card" style={{ padding: '16px' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Medium / Low</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--severity-low)', marginTop: '2px' }}>
                    {bulkResponse.medium_results + bulkResponse.low_results}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Med: {bulkResponse.medium_results} | Low: {bulkResponse.low_results}</div>
                </div>
              </div>

              {/* Validation Errors Box if any */}
              {bulkResponse.validation_errors && bulkResponse.validation_errors.length > 0 && (
                <div className="glass-card" style={{ padding: '20px', marginBottom: '24px', border: '1px solid rgba(244,63,94,0.4)', background: 'rgba(244,63,94,0.08)' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--severity-critical)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertTriangle size={18} />
                    <span>Row Validation Warnings ({bulkResponse.validation_errors.length})</span>
                  </h4>
                  <div style={{ maxHeight: '160px', overflowY: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {bulkResponse.validation_errors.map((err, i) => (
                      <div key={i} style={{ marginBottom: '4px' }}>
                        Row {err.row}: {err.column ? `[${err.column}] ` : ''}{err.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detailed Result Table & Download CSV Button */}
              <div className="glass-card" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ListFilter size={18} color="var(--accent-cyan)" />
                    <span>Bulk Analysis Result Output Table</span>
                  </h4>

                  {/* Download analysis_results.csv */}
                  <a
                    href={analysisAPI.exportCSVUrl}
                    download="analysis_results.csv"
                    className="btn-primary"
                    style={{ padding: '8px 14px', fontSize: '0.8rem', textDecoration: 'none' }}
                  >
                    <Download size={16} />
                    <span>Download analysis_results.csv</span>
                  </a>
                </div>

                <div style={{ overflowX: 'auto', maxHeight: '480px' }}>
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Day</th>
                        <th>Prediction</th>
                        <th>Prediction Prob</th>
                        <th>ML Risk Score</th>
                        <th>Beh Risk Score</th>
                        <th>Final Risk Score</th>
                        <th>Severity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bulkResponse.detailed_results?.map((res, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{res.user}</td>
                          <td style={{ fontSize: '0.8rem' }}>{res.day}</td>
                          <td style={{ fontWeight: 800, color: res.prediction === 1 ? 'var(--severity-critical)' : 'var(--severity-low)' }}>
                            {res.prediction}
                          </td>
                          <td style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                            {(res.prediction_probability * 100).toFixed(2)}%
                          </td>
                          <td>{res.ml_risk_score}</td>
                          <td>{res.behavioral_risk_score}</td>
                          <td style={{ fontWeight: 800, color: 'var(--accent-purple)' }}>{res.final_risk_score}</td>
                          <td>
                            <span className={`badge badge-${res.severity.toLowerCase()}`}>
                              {res.severity}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Feature Importance & High Risk Users Table */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: '32px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={18} color="var(--accent-cyan)" />
            <span>Gradient Boosting Feature Importance</span>
          </h3>
          <div style={{ height: '260px' }}>
            <Bar data={barChartData} options={{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={18} color="var(--severity-critical)" />
            <span>Active High-Risk Monitored Personnel</span>
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>final_risk_score</th>
                  <th>Severity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {(Array.isArray(highRiskUsers) ? highRiskUsers : []).map((u) => {
                  const scoreVal = u.max_risk_score ?? u.risk_score ?? u.display_risk_score ?? 0;
                  const sevLabel = u.latest_severity || u.severity || 'Low';
                  return (
                    <tr key={u.user}>
                      <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{u.user}</td>
                      <td style={{ fontWeight: 800, color: 'var(--severity-critical)' }}>{scoreVal} / 100</td>
                      <td>
                        <span className={`badge badge-${sevLabel.toLowerCase()}`}>{sevLabel}</span>
                      </td>
                      <td>
                        <Link to={`/user-details?user=${u.user}`} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreatDetection;
