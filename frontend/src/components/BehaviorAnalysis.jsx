import { useState, useEffect, useRef } from "react";
import PredictionForm from "./PredictionForm";
import ResultCard from "./ResultCard";
import {
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

function BehaviorAnalysis({ recentAnalyses = [], setRecentAnalyses, selectedEmployee, setSelectedEmployee }) {
  const [mode, setMode] = useState("LIVE");
  const [predictionResult, setPredictionResult] = useState(null);
  const [latestLiveResult, setLatestLiveResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [wsStatus, setWsStatus] = useState("DISCONNECTED");
  const [isLiveMonitoring, setIsLiveMonitoring] = useState(false);

  const [liveStats, setLiveStats] = useState({
    records: 0,
    normal: 0,
    anomaly: 0,
    currentEmp: "-",
    riskLevel: "-",
    lastDetectionTime: "-"
  });

  const [eventStream, setEventStream] = useState([]);
  const [activityTrend, setActivityTrend] = useState([]);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [currentTime, setCurrentTime] = useState(Date.now());

  const wsRef = useRef(null);

  useEffect(() => {
    let interval;
    if (isLiveMonitoring) {
      interval = setInterval(() => {
        setCurrentTime(Date.now());
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isLiveMonitoring]);

  const elapsedSeconds = sessionStartTime ? (currentTime - sessionStartTime) / 1000 : 0;
  const eventsPerSecond = elapsedSeconds > 0 ? (liveStats.records / elapsedSeconds).toFixed(1) : 0;
  const anomalyRate = liveStats.records > 0 ? ((liveStats.anomaly / liveStats.records) * 100).toFixed(1) : "0.0";

  const addRecentAnalysis = (analysis) => {
    if (setRecentAnalyses) {
      setRecentAnalyses((prev) => {
        if (!analysis.timestamp) {
          analysis.timestamp = new Date().toLocaleTimeString();
        }
        return [analysis, ...prev];
      });
    }
  };

  const startLiveMonitoring = () => {
    setLiveStats({
      records: 0,
      normal: 0,
      anomaly: 0,
      currentEmp: "-",
      riskLevel: "-",
      lastDetectionTime: "-"
    });
    setLatestLiveResult(null);
    setEventStream([]);
    setActivityTrend([]);
    setSessionStartTime(Date.now());
    setCurrentTime(Date.now());
    setIsLiveMonitoring(true);
    setWsStatus("CONNECTING...");

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/stream");
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("CONNECTED");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const timestampStr = new Date().toLocaleTimeString();
      const resultFormatted = data.prediction === "ANOMALY" ? "ANOMALY" : "NORMAL";

      setLiveStats(prev => {
        const newRecords = prev.records + 1;

        setActivityTrend(prevTrend => {
          const newTrend = [...prevTrend, { time: timestampStr, records: newRecords }];
          if (newTrend.length > 20) newTrend.shift();
          return newTrend;
        });

        return {
          records: newRecords,
          normal: data.prediction === "NORMAL" ? prev.normal + 1 : prev.normal,
          anomaly: data.prediction === "ANOMALY" ? prev.anomaly + 1 : prev.anomaly,
          currentEmp: data.employeeId,
          riskLevel: data.riskLevel,
          lastDetectionTime: timestampStr
        };
      });

      setLatestLiveResult(resultFormatted);

      setEventStream(prevStream => {
        const newEvent = {
          time: timestampStr,
          employee: data.employeeId,
          prediction: resultFormatted,
          riskLevel: data.riskLevel
        };
        const newStream = [newEvent, ...prevStream];
        if (newStream.length > 10) newStream.pop();
        return newStream;
      });

      addRecentAnalysis({
        employeeId: data.employeeId,
        prediction: resultFormatted,
        riskLevel: data.riskLevel,
        activity: data.activity,
        timestamp: timestampStr,
        status: "LIVE STREAM",
        source: "LIVE"
      });
    };

    ws.onclose = () => {
      setWsStatus("DISCONNECTED");
    };

    ws.onerror = () => {
      setWsStatus("ERROR");
    };
  };

  const stopLiveMonitoring = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsLiveMonitoring(false);
    setWsStatus("STOPPED");
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (mode === "MANUAL" && isLiveMonitoring) {
      stopLiveMonitoring();
    }
  }, [mode, isLiveMonitoring]);

  const getStatusColor = () => {
    if (wsStatus === "CONNECTED") return "var(--accent-success, #10b981)";
    if (wsStatus === "ERROR") return "var(--accent-warning, #ef4444)";
    return "var(--text-secondary)";
  };

  const predictionData = [
    { name: 'NORMAL', value: liveStats.normal },
    { name: 'ANOMALY', value: liveStats.anomaly }
  ];

  const PIE_COLORS = ['#10b981', '#f59e0b'];

  return (
    <div className="behavior-analysis-container">
      <div className="page-header">
        <div className="header-title-row">
          <h1>Behavior Analysis</h1>
          <div className="live-indicator">
            <span className={`status-dot ${wsStatus === 'CONNECTED' ? 'pulsing' : ''}`} style={{ backgroundColor: getStatusColor() }}></span>
            <span style={{ color: getStatusColor() }}>{wsStatus}</span>
          </div>
        </div>
        <p className="page-subtitle">Evaluate employee activity patterns using behavioral intelligence models.</p>
      </div>

      <div className="mode-toggle-container" style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button
          className={`mode-btn ${mode === 'LIVE' ? 'active' : ''}`}
          onClick={() => setMode('LIVE')}
          style={{ padding: '0.75rem 1.5rem', borderRadius: '4px', cursor: 'pointer', background: mode === 'LIVE' ? 'var(--accent-primary)' : 'var(--bg-secondary)', color: 'white', border: 'none', fontWeight: 'bold' }}
        >
          LIVE DATA
        </button>
        <button
          className={`mode-btn ${mode === 'MANUAL' ? 'active' : ''}`}
          onClick={() => setMode('MANUAL')}
          style={{ padding: '0.75rem 1.5rem', borderRadius: '4px', cursor: 'pointer', background: mode === 'MANUAL' ? 'var(--accent-primary)' : 'var(--bg-secondary)', color: 'white', border: 'none', fontWeight: 'bold' }}
        >
          MANUAL TEST
        </button>
      </div>

      {mode === "LIVE" ? (
        <div className="live-dashboard" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Controls */}
          <div className="card" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'var(--bg-secondary)' }}>
            {!isLiveMonitoring && wsStatus !== "STOPPED" && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ fontWeight: 'bold', color: 'var(--text-secondary)' }}>READY FOR LIVE MONITORING</div>
                <button onClick={startLiveMonitoring} style={{ padding: '0.6rem 1.5rem', background: 'var(--accent-primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>▶</span> START LIVE MONITORING
                </button>
              </div>
            )}

            {isLiveMonitoring && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ fontWeight: 'bold', color: 'var(--accent-success, #10b981)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="status-dot pulsing" style={{ backgroundColor: 'var(--accent-success, #10b981)' }}></span> LIVE MONITORING ACTIVE
                </div>
                <button onClick={stopLiveMonitoring} style={{ padding: '0.6rem 1.5rem', background: 'transparent', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>⏹</span> STOP MONITORING
                </button>
              </div>
            )}

            {!isLiveMonitoring && wsStatus === "STOPPED" && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ fontWeight: 'bold', color: 'var(--text-secondary)' }}>MONITORING STOPPED</div>
                <button onClick={startLiveMonitoring} style={{ padding: '0.6rem 1.5rem', background: 'var(--accent-primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>▶</span> START NEW SESSION
                </button>
              </div>
            )}
          </div>

          {/* Stats Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>RECORDS PROCESSED</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{liveStats.records}</div>
            </div>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>NORMAL BEHAVIOR</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-success, #10b981)' }}>{liveStats.normal}</div>
            </div>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>ANOMALIES DETECTED</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-warning, #f59e0b)' }}>{liveStats.anomaly}</div>
            </div>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>ANOMALY RATE</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: liveStats.anomaly > 0 ? 'var(--accent-warning, #f59e0b)' : 'var(--accent-success, #10b981)' }}>
                {anomalyRate}%
              </div>
            </div>
            <div className="card" style={{ padding: '1rem', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>EVENTS / SEC</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{eventsPerSecond}</div>
            </div>
          </div>

          {/* Charts and Alerts Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

            {/* Left Col: Charts */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="card" style={{ padding: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Live Prediction Distribution</h3>
                <div style={{ height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={predictionData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={5} dataKey="value">
                        {predictionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card" style={{ padding: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Live Activity Trend</h3>
                <div style={{ height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={activityTrend} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{ fontSize: 10 }} />
                      <YAxis stroke="var(--text-secondary)" tick={{ fontSize: 10 }} />
                      <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }} />
                      <Line type="monotone" dataKey="records" stroke="var(--accent-primary)" strokeWidth={2} dot={false} isAnimationActive={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Right Col: Alerts */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="card" style={{
                padding: '1.5rem',
                border: latestLiveResult === 'ANOMALY' ? '2px solid var(--accent-warning, #f59e0b)' : '1px solid var(--border-color)',
                backgroundColor: latestLiveResult === 'ANOMALY' ? 'rgba(245, 158, 11, 0.05)' : 'var(--bg-secondary)',
                transition: 'all 0.3s ease'
              }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Real-Time Threat Alert</h3>
                {latestLiveResult === 'ANOMALY' ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', animation: 'pulse 2s infinite' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-warning, #f59e0b)' }}>ANOMALY DETECTED</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.5rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Employee ID:</span>
                      <span style={{ fontWeight: 'bold' }}>{liveStats.currentEmp}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Risk Level:</span>
                      <span style={{ fontWeight: 'bold', color: 'var(--accent-warning, #f59e0b)' }}>{liveStats.riskLevel}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Detection Time:</span>
                      <span>{liveStats.lastDetectionTime}</span>
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '2rem 1rem', textAlign: 'center' }}>
                    <div style={{ color: 'var(--accent-success, #10b981)', fontSize: '1.2rem', fontWeight: 'bold' }}>BEHAVIORAL ACTIVITY NORMAL</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>Monitoring for suspicious patterns...</div>
                  </div>
                )}
              </div>

              <div className="card" style={{ padding: '1.5rem' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Current Employee</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>CURRENTLY ANALYZED</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', fontFamily: 'monospace' }}>{liveStats.currentEmp}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                    <div style={{ flex: 1, padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: '4px' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.7rem' }}>PREDICTION</div>
                      <div style={{ fontWeight: 'bold', color: latestLiveResult === 'ANOMALY' ? 'var(--accent-warning, #f59e0b)' : (latestLiveResult === 'NORMAL' ? 'var(--accent-success, #10b981)' : 'var(--text-primary)') }}>
                        {latestLiveResult || "-"}
                      </div>
                    </div>
                    <div style={{ flex: 1, padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: '4px' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.7rem' }}>RISK LEVEL</div>
                      <div style={{ fontWeight: 'bold', color: liveStats.riskLevel === 'HIGH' ? 'var(--accent-warning, #f59e0b)' : (liveStats.riskLevel === 'LOW' ? 'var(--accent-success, #10b981)' : 'var(--text-primary)') }}>
                        {liveStats.riskLevel}
                      </div>
                    </div>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textAlign: 'right', marginTop: '0.5rem' }}>
                    Last Detection Time: {liveStats.lastDetectionTime}
                  </div>
                </div>
              </div>

              <div className="card">
                <h2 className="card-header">Model Intelligence</h2>
                <div className="model-info-content" style={{ padding: '1rem' }}>
                  <div className="model-info-item">
                    <span className="info-label">Primary Model</span>
                    <span className="info-value">Isolation Forest</span>
                  </div>
                  <div className="model-info-item">
                    <span className="info-label">Stream Source</span>
                    <span className="info-value">Processed Feature Pipeline</span>
                  </div>
                  <p className="model-info-desc" style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                    Behavioral activity features are evaluated to identify anomalous patterns. Unsupervised anomaly detection classifies records as NORMAL or ANOMALY.
                  </p>
                </div>
              </div>

            </div>
          </div>

          {/* Event Stream */}
          <div className="card" style={{ padding: '0' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
              <h3 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>LIVE EVENT STREAM</h3>
            </div>
            {eventStream.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Waiting for events...</div>
            ) : (
              <div className="table-responsive">
                <table className="data-table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>TIME</th>
                      <th style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>EMPLOYEE</th>
                      <th style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>PREDICTION</th>
                      <th style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>RISK</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eventStream.map((evt, idx) => (
                      <tr key={idx} style={{ backgroundColor: evt.prediction === 'ANOMALY' ? 'rgba(245, 158, 11, 0.05)' : 'transparent' }}>
                        <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)' }}>{evt.time}</td>
                        <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', fontFamily: 'monospace', fontWeight: 'bold' }}>{evt.employee}</td>
                        <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', fontWeight: 'bold', color: evt.prediction === 'ANOMALY' ? 'var(--accent-warning, #f59e0b)' : 'var(--accent-success, #10b981)' }}>{evt.prediction}</td>
                        <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)' }}>
                          <span className={`status-pill ${evt.riskLevel === 'HIGH' ? 'danger' : 'normal'}`}>{evt.riskLevel}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      ) : (
        <div className="dashboard-grid-ba">
          <div className="analysis-left-col">
            <div className="card">
              <h2 className="card-header">Manual Input</h2>
              <PredictionForm
                setPredictionResult={setPredictionResult}
                setIsLoading={setIsLoading}
                isLoading={isLoading}
                addRecentAnalysis={(res) => addRecentAnalysis({ ...res, source: 'MANUAL' })}
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
                  <span className="info-label">Stream Source</span>
                  <span className="info-value">Processed Feature Pipeline</span>
                </div>
                <p className="model-info-desc">
                  Behavioral activity features are evaluated to identify anomalous patterns associated with potential insider-threat activity. Unsupervised anomaly detection classifies records as NORMAL or ANOMALY.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Shared Recent Analysis across both modes (or manual only, based on previous layout, but it was outside the grid) */}
      <div className="card recent-analysis-card" style={{ marginTop: '1.5rem' }}>
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
                  <span className="recent-id" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>[{item.source || 'MANUAL'}]</span>
                  <span className={`recent-result ${item.prediction === "ANOMALY" || item.prediction === "INSIDER" ? 'threat-text' : 'normal-text'}`}>
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
