import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Shield,
  Activity,
  LayoutDashboard,
  Users,
  ChevronRight,
  ChevronDown,
  ArrowRight,
  Clock,
  HardDrive,
  Mail,
  Globe,
  Cloud,
  FileSpreadsheet,
  Monitor,
  Radio,
  Sliders,
  Calendar,
  Layers,
  Pause,
  Play
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, Cell
} from 'recharts';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [userLogs, setUserLogs] = useState([]);
  const [selectedLogIndex, setSelectedLogIndex] = useState(0);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // Backend Pre-Calculated Stats & Feed State
  const [stats, setStats] = useState(null);
  const [feedSeverity, setFeedSeverity] = useState('All');
  const [feedPage, setFeedPage] = useState(1);
  const [feedTotal, setFeedTotal] = useState(0);
  const [feedRecords, setFeedRecords] = useState([]);
  const [streamActive, setStreamActive] = useState(true);

  // Behavior Simulator Custom Input State
  const [simTargetUser, setSimTargetUser] = useState('');
  const [simUserLogs, setSimUserLogs] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const [simInputs, setSimInputs] = useState({
    off_hours_logons: 4,
    logon_count: 8,
    usb_connects: 3,
    off_hours_usb: 2,
    files_copied_to_usb: 10,
    sensitive_files_to_usb: 6,
    external_emails_sent: 12,
    total_emails_sent: 25,
    http_requests: 120,
    cloud_job_visits: 5
  });
  const [simPrediction, setSimPrediction] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 1. Initial Load: Fetch full dashboard stats, users, and initial feed page directly
  useEffect(() => {
    axios.get(`${API_BASE}/api/dashboard/stats`)
      .then(res => setStats(res.data))
      .catch(err => console.error("Error loading dashboard stats:", err));

    axios.get(`${API_BASE}/api/users`)
      .then(res => {
        const fetched = res.data.users || [];
        setUsers(fetched);
        if (fetched.length > 0) {
          setSelectedUser(fetched[0]);
          setSimTargetUser(fetched[0]);
        }
      })
      .catch(err => console.error("Error loading users:", err));
  }, []);

  // 2. Load Feed Data with Pagination & Severity Filtering
  useEffect(() => {
    axios.get(`${API_BASE}/api/feed?page=${feedPage}&limit=15&severity=${feedSeverity}`)
      .then(res => {
        setFeedRecords(res.data.records || []);
        setFeedTotal(res.data.total || 0);
      })
      .catch(err => console.error("Error fetching feed:", err));
  }, [feedPage, feedSeverity]);

  // 3. Activity Replay Ticker
  useEffect(() => {
    if (!streamActive || feedRecords.length === 0) return;

    const interval = setInterval(() => {
      setFeedRecords(prev => {
        if (prev.length <= 1) return prev;
        const [first, ...rest] = prev;
        return [...rest, first];
      });
    }, 1200);

    return () => clearInterval(interval);
  }, [streamActive, feedRecords]);

  // 4. Fetch records when selected user changes in Investigation Workspace
  useEffect(() => {
    if (!selectedUser) return;
    setPrediction(null);
    axios.get(`${API_BASE}/api/users/${selectedUser}/logs`)
      .then(res => {
        const records = res.data.records || [];
        setUserLogs(records);
        setSelectedLogIndex(0);
      })
      .catch(err => console.error("Error fetching user logs:", err));
  }, [selectedUser]);

  // 5. Fetch employee baseline specifically for simulator when target changes
  useEffect(() => {
    if (!simTargetUser) return;
    axios.get(`${API_BASE}/api/users/${simTargetUser}/logs`)
      .then(res => {
        const records = res.data.records || [];
        setSimUserLogs(records);
        if (records.length > 0) {
          const base = records[0];
          setSimInputs(prev => ({
            ...prev,
            off_hours_logons: base.off_hours_logons ?? prev.off_hours_logons,
            logon_count: base.logon_count ?? prev.logon_count,
            usb_connects: base.usb_connects ?? prev.usb_connects,
            off_hours_usb: base.off_hours_usb ?? prev.off_hours_usb,
            files_copied_to_usb: base.files_copied_to_usb ?? prev.files_copied_to_usb,
            sensitive_files_to_usb: base.sensitive_files_to_usb ?? prev.sensitive_files_to_usb,
            external_emails_sent: base.external_emails_sent ?? prev.external_emails_sent,
            total_emails_sent: base.total_emails_sent ?? prev.total_emails_sent,
            http_requests: base.http_requests ?? prev.http_requests,
            cloud_job_visits: base.cloud_job_visits ?? prev.cloud_job_visits
          }));
        }
      })
      .catch(err => console.error("Error fetching simulator target logs:", err));
  }, [simTargetUser]);

  // 6. Run Threat Prediction on active selected record
  const handleAnalyze = () => {
    if (!userLogs.length) return;
    setLoading(true);
    const activeLog = userLogs[selectedLogIndex];

    axios.post(`${API_BASE}/api/predict`, activeLog)
      .then(res => {
        setPrediction(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Prediction error:", err);
        setLoading(false);
      });
  };

  // 7. Run Custom Behavioral Simulator with Employee Baseline
  const handleSimulate = () => {
    const targetUserId = simTargetUser.trim() || "AAE0190";
    const employeeBase = (simUserLogs && simUserLogs.length > 0 ? simUserLogs[0] : null) || (userLogs && userLogs.length > 0 ? userLogs[0] : null) || {
      user: targetUserId,
      day: new Date().toISOString().split('T')[0],
      distinct_pcs: 1,
      total_attachments: 2.0,
      total_email_size: 250000.0,
      role_encoded: 1,
      department_encoded: 1,
      supervisor_encoded: 1,
      historical_events_proxy: 0.0
    };

    const payload = {
      user: String(targetUserId),
      day: String(employeeBase.day || new Date().toISOString().split('T')[0]),
      logon_count: Number(simInputs.logon_count || 1),
      off_hours_logons: Number(simInputs.off_hours_logons || 0),
      distinct_pcs: Number(employeeBase.distinct_pcs || 1),
      usb_connects: Number(simInputs.usb_connects || 0),
      off_hours_usb: Number(simInputs.off_hours_usb || 0),
      files_copied_to_usb: Number(simInputs.files_copied_to_usb || 0),
      sensitive_files_to_usb: Number(simInputs.sensitive_files_to_usb || 0),
      total_emails_sent: Number(simInputs.total_emails_sent || 0),
      external_emails_sent: Number(simInputs.external_emails_sent || 0),
      total_attachments: Number(employeeBase.total_attachments || 0),
      total_email_size: Number(employeeBase.total_email_size || 0),
      http_requests: Number(simInputs.http_requests || 0),
      cloud_job_visits: Number(simInputs.cloud_job_visits || 0),
      role_encoded: Number(employeeBase.role_encoded || 0),
      department_encoded: Number(employeeBase.department_encoded || 0),
      supervisor_encoded: Number(employeeBase.supervisor_encoded || 0),
      historical_events_proxy: Number(employeeBase.historical_events_proxy || 0.0)
    };

    setSimLoading(true);
    axios.post(`${API_BASE}/api/predict`, payload)
      .then(res => {
        setSimPrediction(res.data);
        setSimLoading(false);
      })
      .catch(err => {
        console.error("Simulation error:", err);
        setSimLoading(false);
      });
  };

  const getSeverityStyle = (sev) => {
    switch (sev) {
      case 'Critical':
        return {
          badge: 'bg-red-500/15 text-red-400 border-red-500/40',
          bar: 'bg-red-500',
          text: 'text-red-400',
          color: '#ef4444'
        };
      case 'High':
        return {
          badge: 'bg-orange-500/15 text-orange-400 border-orange-500/40',
          bar: 'bg-orange-500',
          text: 'text-orange-400',
          color: '#f97316'
        };
      case 'Medium':
        return {
          badge: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/40',
          bar: 'bg-yellow-500',
          text: 'text-yellow-400',
          color: '#eab308'
        };
      default:
        return {
          badge: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40',
          bar: 'bg-emerald-500',
          text: 'text-emerald-400',
          color: '#22c55e'
        };
    }
  };

  const realDistributionData = stats ? [
    { name: 'Low', count: stats.severity_distribution.Low, color: '#22c55e' },
    { name: 'Medium', count: stats.severity_distribution.Medium, color: '#eab308' },
    { name: 'High', count: stats.severity_distribution.High, color: '#f97316' },
    { name: 'Critical', count: stats.severity_distribution.Critical, color: '#ef4444' }
  ] : [];

  const activeRecord = userLogs[selectedLogIndex] || null;
  const matchingSimUsers = users.filter(u => u.toLowerCase().includes(simTargetUser.toLowerCase()));

  return (
    <div className="min-h-screen bg-[#070a13] text-slate-200 font-sans flex text-base antialiased selection:bg-indigo-500/30">

      {/* 🧭 SIDEBAR NAVIGATION */}
      <aside className="w-72 bg-[#0c101d] border-r border-slate-800/80 p-6 flex flex-col justify-between shrink-0">
        <div className="space-y-8">
          <div className="flex items-center gap-3.5 px-1 py-1">
            <div className="p-2.5 bg-indigo-600/20 border border-indigo-500/40 rounded-xl shadow-inner">
              <Shield className="w-7 h-7 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wider text-white uppercase">INSIDER WATCH</h1>
              <p className="text-xs text-slate-400 font-mono">Threat Intelligence</p>
            </div>
          </div>

          <nav className="space-y-6">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mb-2.5">Overview</p>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition ${activeTab === 'dashboard' ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
              >
                <LayoutDashboard className="w-5 h-5" /> Executive Dashboard
              </button>
            </div>

            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mb-2.5">Monitoring</p>
              <div className="space-y-1.5">
                <button
                  onClick={() => setActiveTab('stream')}
                  className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition ${activeTab === 'stream' ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
                >
                  <Radio className="w-5 h-5" /> Session Threat Feed
                </button>
              </div>
            </div>

            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mb-2.5">Investigation</p>
              <div className="space-y-1.5">
                <button
                  onClick={() => setActiveTab('investigate')}
                  className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition ${activeTab === 'investigate' ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
                >
                  <Activity className="w-5 h-5" /> Threat Analysis
                </button>
                <button
                  onClick={() => setActiveTab('simulator')}
                  className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition ${activeTab === 'simulator' ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 shadow-sm' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
                >
                  <Sliders className="w-5 h-5" /> Behavior Simulator
                </button>
              </div>
            </div>
          </nav>
        </div>
      </aside>

      {/* 🚀 MAIN CONTENT CONSOLE */}
      <div className="flex-1 flex flex-col min-w-0">

        <header className="h-16 border-b border-slate-800/80 bg-[#0c101d]/60 px-8 flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-2.5 text-slate-400 text-sm">
            <span>Security Console</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-slate-100 font-semibold text-base capitalize">
              {activeTab === 'dashboard' && 'Executive Dashboard'}
              {activeTab === 'stream' && 'Session Threat Feed'}
              {activeTab === 'investigate' && 'Incident Investigation Workspace'}
              {activeTab === 'simulator' && 'Custom Behavior Simulator'}
            </span>
          </div>
        </header>

        <main className="p-8 overflow-y-auto flex-1 space-y-8">

          {/* ================= PAGE 1: 📊 EXECUTIVE DASHBOARD ================= */}
          {activeTab === 'dashboard' && stats && (
            <div className="space-y-8 w-full">

              {/* Top 4 KPI Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-[#0c101d] border border-slate-800/90 p-6 rounded-2xl space-y-2">
                  <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Monitored Employees</p>
                  <p className="text-4xl font-extrabold text-white font-mono">{stats.total_users}</p>
                  <p className="text-xs text-indigo-400 font-sans font-medium">Active Identity Pool</p>
                </div>

                <div className="bg-[#0c101d] border border-slate-800/90 p-6 rounded-2xl space-y-2">
                  <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Evaluated Sessions</p>
                  <p className="text-4xl font-extrabold text-slate-100 font-mono">{stats.total_sessions}</p>
                  <p className="text-xs text-slate-400 font-sans font-medium">All Activity Records</p>
                </div>

                <div className="bg-[#0c101d] border border-slate-800/90 p-6 rounded-2xl space-y-2">
                  <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">High / Critical Flags</p>
                  <p className="text-4xl font-extrabold text-red-400 font-mono">
                    {stats.high_count + stats.critical_count}
                  </p>
                  <p className="text-xs text-red-400 font-sans font-medium">
                    {stats.high_count} High · {stats.critical_count} Critical
                  </p>
                </div>

                <div className="bg-[#0c101d] border border-slate-800/90 p-6 rounded-2xl space-y-2">
                  <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Average Risk Score</p>
                  <p className="text-4xl font-extrabold text-amber-400 font-mono">{stats.avg_risk}%</p>
                  <p className="text-xs text-slate-400 font-sans font-medium">Org Behavioral Baseline</p>
                </div>
              </div>

              {/* Real Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Risk Distribution */}
                <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl space-y-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider">
                        Risk Distribution Across Evaluated Sessions
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">All evaluated activity records</p>
                    </div>
                  </div>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={realDistributionData}>
                        <XAxis dataKey="name" stroke="#94a3b8" fontSize={13} />
                        <YAxis stroke="#94a3b8" fontSize={13} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '10px', fontSize: '13px' }} />
                        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                          {realDistributionData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Smooth Weekly Resampled Organizational Risk Trend */}
                <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl space-y-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider">
                        Organizational Risk Trend
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">Weekly aggregate behavioral threat trajectory</p>
                    </div>
                  </div>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={stats.trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.45} />
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <XAxis
                          dataKey="session"
                          stroke="#64748b"
                          fontSize={11}
                          tickLine={false}
                          tickFormatter={(val) => {
                            const d = new Date(val);
                            return `${d.toLocaleString('en-US', { month: 'short' })} '${String(d.getFullYear()).slice(2)}`;
                          }}
                          minTickGap={45}
                        />
                        <YAxis
                          stroke="#64748b"
                          fontSize={12}
                          domain={[0, 100]}
                          tickLine={false}
                          axisLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '10px',
                            fontSize: '13px'
                          }}
                          formatter={(val) => [`${val}%`, 'Weekly Avg Risk']}
                          labelFormatter={(label) => `Week of ${label}`}
                        />
                        <Area
                          type="natural"
                          dataKey="risk"
                          stroke="#6366f1"
                          strokeWidth={2.5}
                          fill="url(#riskGradient)"
                          dot={false}
                          activeDot={{ r: 5, fill: '#818cf8', stroke: '#070a13', strokeWidth: 2 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>

              {/* Priority Targets Table */}
              <div className="bg-[#0c101d] border border-slate-800/90 rounded-2xl overflow-hidden shadow-sm">
                <div className="p-6 border-b border-slate-800/90 flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider">Top Evaluated Targets</h3>
                    <p className="text-xs text-slate-400 mt-1">Prioritized identities ranked by evaluated threat severity</p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse font-sans text-sm">
                    <thead className="bg-[#080c18] border-b border-slate-800/80 text-slate-400 uppercase text-xs">
                      <tr>
                        <th className="py-4 px-6 font-bold">Employee ID</th>
                        <th className="py-4 px-6 font-bold">Session Date</th>
                        <th className="py-4 px-6 font-bold">Key Activity Summary</th>
                        <th className="py-4 px-6 font-bold">Overall Risk</th>
                        <th className="py-4 px-6 font-bold">Threat Level</th>
                        <th className="py-4 px-6 font-bold text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {stats.top_targets.map((item) => {
                        const style = getSeverityStyle(item.severity);
                        return (
                          <tr key={`${item.user}-${item.day}`} className="hover:bg-slate-800/30 transition">
                            <td className="py-4 px-6 font-mono font-bold text-indigo-400 text-base">{item.user}</td>
                            <td className="py-4 px-6 font-mono text-slate-300">{item.day}</td>
                            <td className="py-4 px-6 text-slate-300">
                              {item.sensitive_files_to_usb > 0
                                ? `USB Exfiltration (${item.sensitive_files_to_usb} sensitive files)`
                                : item.off_hours_logons > 0
                                  ? `After-hours activity (${item.off_hours_logons} logins)`
                                  : `Standard traffic (${item.external_emails_sent} external emails)`}
                            </td>
                            <td className="py-4 px-6">
                              <div className="flex items-center gap-2.5">
                                <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
                                  <div className={`h-full ${style.bar}`} style={{ width: `${Math.min(item.overall_risk_score, 100)}%` }}></div>
                                </div>
                                <span className="font-mono font-bold text-slate-100">{item.overall_risk_score}%</span>
                              </div>
                            </td>
                            <td className="py-4 px-6">
                              <span className={`px-3 py-1 rounded-md text-xs font-bold border uppercase ${style.badge}`}>
                                {item.severity}
                              </span>
                            </td>
                            <td className="py-4 px-6 text-right">
                              <button
                                onClick={() => {
                                  setSelectedUser(item.user);
                                  setActiveTab('investigate');
                                }}
                                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition inline-flex items-center gap-1.5"
                              >
                                Investigate <ArrowRight className="w-4 h-4 text-indigo-400" />
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
          )}

          {/* ================= PAGE 2: 🔴 SESSION THREAT FEED ================= */}
          {activeTab === 'stream' && (
            <div className="space-y-6 w-full">

              <div className="bg-[#0c101d] border border-slate-800/90 p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-white uppercase tracking-wider">Session Threat Feed</h2>
                  <p className="text-xs text-slate-400 mt-1">Historical activity replayed through the threat detection pipeline</p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 bg-[#070a13] p-1 rounded-xl border border-slate-800">
                    {['All', 'Critical', 'High', 'Medium', 'Low'].map((sev) => (
                      <button
                        key={sev}
                        onClick={() => {
                          setFeedSeverity(sev);
                          setFeedPage(1);
                        }}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${feedSeverity === sev ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                      >
                        {sev}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => setStreamActive(!streamActive)}
                    className={`px-4 py-2 rounded-xl font-semibold text-xs transition flex items-center gap-2 ${streamActive ? 'bg-amber-500/20 border border-amber-500/40 text-amber-300' : 'bg-emerald-600 text-white'}`}
                  >
                    {streamActive ? <><Pause className="w-4 h-4" /> Pause Feed</> : <><Play className="w-4 h-4" /> Resume Feed</>}
                  </button>
                </div>
              </div>

              <div className="bg-[#0c101d] border border-slate-800/90 rounded-2xl overflow-hidden shadow-sm">
                <div className="p-4 bg-[#080c18] border-b border-slate-800/90 flex items-center justify-between text-xs text-slate-400">
                  <span>Showing <strong>{feedRecords.length}</strong> of <strong>{feedTotal}</strong> records</span>
                  <div className="flex items-center gap-2">
                    <button
                      disabled={feedPage === 1}
                      onClick={() => setFeedPage(p => Math.max(1, p - 1))}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded text-xs text-white"
                    >
                      Previous
                    </button>
                    <span className="font-mono">Page {feedPage}</span>
                    <button
                      disabled={feedPage * 15 >= feedTotal}
                      onClick={() => setFeedPage(p => p + 1)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded text-xs text-white"
                    >
                      Next
                    </button>
                  </div>
                </div>

                <table className="w-full text-left border-collapse font-mono text-sm">
                  <thead className="bg-[#080c18]/50 border-b border-slate-800/80 text-slate-400 uppercase text-xs">
                    <tr>
                      <th className="py-4 px-6 font-bold">User Entity</th>
                      <th className="py-4 px-6 font-bold">Session Date</th>
                      <th className="py-4 px-6 font-bold">Activity Features</th>
                      <th className="py-4 px-6 font-bold">Overall Risk</th>
                      <th className="py-4 px-6 font-bold">Threat Level</th>
                      <th className="py-4 px-6 font-bold text-right font-sans">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {feedRecords.map((ev) => {
                      const style = getSeverityStyle(ev.severity);
                      return (
                        <tr key={`${ev.user}-${ev.day}`} className="hover:bg-slate-800/30 transition">
                          <td className="py-4 px-6 font-mono font-bold text-indigo-400">{ev.user}</td>
                          <td className="py-4 px-6 font-mono text-slate-300">{ev.day}</td>
                          <td className="py-4 px-6 text-slate-300 text-sm">
                            Logons: {ev.logon_count} | USB: {ev.usb_connects} | Emails: {ev.external_emails_sent}
                          </td>
                          <td className="py-4 px-6 font-mono font-bold text-slate-100">
                            {ev.overall_risk_score}%
                          </td>
                          <td className="py-4 px-6">
                            <span className={`px-3 py-1 rounded-md text-xs font-bold border uppercase ${style.badge}`}>
                              {ev.severity}
                            </span>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <button
                              onClick={() => {
                                setSelectedUser(ev.user);
                                setActiveTab('investigate');
                              }}
                              className="text-indigo-400 hover:text-indigo-300 underline font-semibold text-xs"
                            >
                              Investigate
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

            </div>
          )}

          {/* ================= PAGE 3: 🔍 INCIDENT INVESTIGATION ================= */}
          {activeTab === 'investigate' && (
            <div className="space-y-8 w-full">

              <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl flex flex-wrap items-end justify-between gap-6 shadow-sm">
                <div className="flex flex-wrap items-center gap-6">
                  <div>
                    <label className="text-sm text-slate-400 block mb-2 font-semibold flex items-center gap-2">
                      <Users className="w-4 h-4 text-indigo-400" /> Target Employee Identifier
                    </label>
                    <select
                      value={selectedUser}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      className="bg-[#070a13] border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none min-w-[240px]"
                    >
                      {users.map(u => <option key={u} value={u}>{u}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 block mb-2 font-semibold flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-indigo-400" /> Available Session Date
                    </label>
                    <select
                      value={selectedLogIndex}
                      onChange={(e) => {
                        setSelectedLogIndex(Number(e.target.value));
                        setPrediction(null);
                      }}
                      className="bg-[#070a13] border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none min-w-[280px]"
                    >
                      {userLogs.map((log, idx) => (
                        <option key={idx} value={idx}>
                          Date: {log.day} {idx === 0 ? '(Highest Threat Day)' : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleAnalyze}
                  disabled={loading || !userLogs.length}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-6 py-3 rounded-xl transition duration-200 flex items-center gap-2.5 shadow-lg shadow-indigo-600/20 disabled:opacity-50 text-sm"
                >
                  <Activity className="w-5 h-5" /> {loading ? 'Evaluating Model...' : 'Run Threat Assessment'}
                </button>
              </div>

              {prediction ? (
                <div className="space-y-6">
                  <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl flex flex-wrap items-center justify-between gap-6 shadow-sm">
                    <div className="space-y-1.5">
                      <span className="text-xs text-slate-400 uppercase tracking-widest font-mono font-bold">ASSESSMENT RESULT</span>
                      <h2 className="text-3xl font-bold font-mono text-white flex items-center gap-2.5">
                        {prediction.user}
                        <span className="text-base font-normal text-slate-400 font-sans">({prediction.day})</span>
                      </h2>
                      <p className="text-sm text-slate-400">Behavioral activity evaluated against baseline</p>
                    </div>

                    <div className="flex items-center gap-14">
                      <div className="text-right space-y-1.5">
                        <p className="text-sm text-slate-400 font-semibold">Overall Risk Score</p>
                        <div className="flex items-baseline justify-end gap-1 font-mono">
                          <span className="text-4xl font-extrabold text-white">{prediction.overall_risk_score}</span>
                          <span className="text-slate-400 text-lg font-semibold">%</span>
                        </div>
                        <div className="w-36 h-2.5 bg-slate-800 rounded-full overflow-hidden ml-auto">
                          <div className={`h-full ${getSeverityStyle(prediction.severity).bar}`} style={{ width: `${Math.min(prediction.overall_risk_score, 100)}%` }}></div>
                        </div>
                      </div>

                      <div className="text-right space-y-1.5">
                        <p className="text-sm text-slate-400 font-semibold">Threat Level</p>
                        <span className={`inline-block px-4 py-1.5 rounded-lg text-sm font-extrabold uppercase border ${getSeverityStyle(prediction.severity).badge}`}>
                          {prediction.severity}
                        </span>
                        <p className="text-xs text-slate-400 font-mono">Status Verified</p>
                      </div>
                    </div>
                  </div>

                  {activeRecord && (
                    <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl space-y-5">
                      <div className="flex items-center justify-between border-b border-slate-800/90 pb-4">
                        <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2.5">
                          <Layers className="w-5 h-5 text-indigo-400" /> Monitored Session Behavioral Telemetry
                        </h3>
                        <span className="text-xs text-slate-400 font-mono">Day ID: {prediction.day}</span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Clock className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>After-Hours Logins</span>
                          </div>
                          <p className="text-3xl font-bold font-mono text-white">{activeRecord.off_hours_logons}</p>
                          <p className="text-xs text-slate-400">Total: {activeRecord.logon_count} logins</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <HardDrive className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>USB Insertions</span>
                          </div>
                          <p className="text-3xl font-bold font-mono text-white">{activeRecord.usb_connects}</p>
                          <p className="text-xs text-slate-400">{activeRecord.off_hours_usb} off-hours USB</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <FileSpreadsheet className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>Restricted Files to USB</span>
                          </div>
                          <p className={`text-3xl font-bold font-mono ${activeRecord.sensitive_files_to_usb > 0 ? 'text-red-400' : 'text-white'}`}>
                            {activeRecord.sensitive_files_to_usb}
                          </p>
                          <p className="text-xs text-slate-400">{activeRecord.files_copied_to_usb} total copied</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Mail className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>External Emails Sent</span>
                          </div>
                          <p className={`text-3xl font-bold font-mono ${activeRecord.external_emails_sent > 5 ? 'text-orange-400' : 'text-white'}`}>
                            {activeRecord.external_emails_sent}
                          </p>
                          <p className="text-xs text-slate-400">{activeRecord.total_emails_sent} total emails</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Globe className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>HTTP Requests</span>
                          </div>
                          <p className="text-3xl font-bold font-mono text-white">{activeRecord.http_requests}</p>
                          <p className="text-xs text-slate-400">Total browser hits</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Cloud className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>Cloud / Job Visits</span>
                          </div>
                          <p className={`text-3xl font-bold font-mono ${activeRecord.cloud_job_visits > 0 ? 'text-amber-400' : 'text-white'}`}>
                            {activeRecord.cloud_job_visits}
                          </p>
                          <p className="text-xs text-slate-400">Cloud storage hits</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Monitor className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>Workstations Used</span>
                          </div>
                          <p className="text-3xl font-bold font-mono text-white">{activeRecord.distinct_pcs}</p>
                          <p className="text-xs text-slate-400">Distinct machine endpoints</p>
                        </div>

                        <div className="bg-[#070a13] p-5 rounded-2xl border border-slate-800/80 space-y-2">
                          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold">
                            <Mail className="w-4 h-4 text-indigo-400 shrink-0" />
                            <span>Outbound Email Size</span>
                          </div>
                          <p className="text-3xl font-bold font-mono text-white">
                            {(activeRecord.total_email_size / 1024).toFixed(1)} <span className="text-sm text-slate-400 font-normal">KB</span>
                          </p>
                          <p className="text-xs text-slate-400">Total egress volume</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-[#0c101d] border border-dashed border-slate-800 p-16 rounded-2xl text-center text-slate-400 space-y-3.5">
                  <Activity className="w-12 h-12 text-slate-500 mx-auto" />
                  <p className="text-slate-200 font-bold text-lg">Select an employee and session date</p>
                  <p className="text-sm text-slate-400 max-w-lg mx-auto">
                    Click "Run Threat Assessment" above to evaluate session threat risk and telemetry indicators.
                  </p>
                </div>
              )}

            </div>
          )}

          {/* ================= PAGE 4: 🧑‍💻 BEHAVIOR SIMULATOR ================= */}
          {activeTab === 'simulator' && (
            <div className="space-y-8 w-full">

              <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl space-y-2">
                <h2 className="text-lg font-bold text-white uppercase tracking-wider">Custom Behavior Simulator</h2>
                <p className="text-sm text-slate-400">
                  Select or type any monitored Employee ID to dynamically load their baseline telemetry, then adjust parameters to evaluate session threat risk.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                <div className="lg:col-span-2 bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl space-y-6">
                  <div className="flex flex-wrap items-center justify-between border-b border-slate-800/80 pb-4 gap-4">
                    <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider">
                      Input Activity Parameters
                    </h3>

                    <div className="flex items-center gap-3 relative" ref={dropdownRef}>
                      <label className="text-sm text-slate-400 font-semibold flex items-center gap-1.5">
                        <Users className="w-4 h-4 text-indigo-400" /> Employee ID:
                      </label>

                      <div className="relative">
                        <input
                          type="text"
                          value={simTargetUser}
                          onChange={(e) => {
                            setSimTargetUser(e.target.value);
                            setIsDropdownOpen(true);
                          }}
                          onFocus={() => setIsDropdownOpen(true)}
                          className="bg-[#070a13] border border-slate-700 rounded-xl pl-3.5 pr-8 py-2 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none w-48 shadow-inner"
                        />
                        <button
                          type="button"
                          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </button>

                        {isDropdownOpen && (
                          <div className="absolute left-0 top-full mt-1.5 w-48 bg-[#0c101d] border border-slate-700 rounded-xl shadow-2xl z-50 max-h-56 overflow-y-auto font-mono text-sm py-1 divide-y divide-slate-800/50">
                            {matchingSimUsers.length > 0 ? (
                              matchingSimUsers.map(u => (
                                <button
                                  key={u}
                                  type="button"
                                  onClick={() => {
                                    setSimTargetUser(u);
                                    setIsDropdownOpen(false);
                                  }}
                                  className={`w-full text-left px-3.5 py-2 hover:bg-indigo-600/20 hover:text-indigo-300 transition ${simTargetUser === u ? 'bg-indigo-600/30 text-indigo-300 font-bold' : 'text-slate-300'}`}
                                >
                                  {u}
                                </button>
                              ))
                            ) : (
                              <div className="px-3.5 py-2 text-xs text-slate-400">
                                No matching IDs
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">1. After-Hours Logins</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.off_hours_logons}
                        onChange={(e) => setSimInputs({ ...simInputs, off_hours_logons: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">2. Total Daily Logons</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.logon_count}
                        onChange={(e) => setSimInputs({ ...simInputs, logon_count: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">3. USB Device Insertions</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.usb_connects}
                        onChange={(e) => setSimInputs({ ...simInputs, usb_connects: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">4. After-Hours USB Connects</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.off_hours_usb}
                        onChange={(e) => setSimInputs({ ...simInputs, off_hours_usb: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">5. Total Files Copied to USB</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.files_copied_to_usb}
                        onChange={(e) => setSimInputs({ ...simInputs, files_copied_to_usb: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">6. Restricted Files Copied to USB</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.sensitive_files_to_usb}
                        onChange={(e) => setSimInputs({ ...simInputs, sensitive_files_to_usb: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">7. Outbound External Emails</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.external_emails_sent}
                        onChange={(e) => setSimInputs({ ...simInputs, external_emails_sent: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">8. Total Daily Emails Sent</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.total_emails_sent}
                        onChange={(e) => setSimInputs({ ...simInputs, total_emails_sent: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">9. HTTP Web Requests</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.http_requests}
                        onChange={(e) => setSimInputs({ ...simInputs, http_requests: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1.5 font-semibold">10. Cloud Storage / Job Visits</label>
                      <input
                        type="number"
                        min="0"
                        value={simInputs.cloud_job_visits}
                        onChange={(e) => setSimInputs({ ...simInputs, cloud_job_visits: e.target.value })}
                        className="w-full bg-[#070a13] border border-slate-700 rounded-xl p-2.5 text-sm text-white font-mono focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleSimulate}
                    disabled={simLoading}
                    className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 rounded-xl transition duration-200 flex items-center justify-center gap-2.5 text-sm shadow-md shadow-indigo-600/20"
                  >
                    <Sliders className="w-5 h-5" /> {simLoading ? 'Evaluating Model...' : 'Analyze Behavior'}
                  </button>
                </div>

                <div className="bg-[#0c101d] border border-slate-800/90 p-7 rounded-2xl flex flex-col justify-center space-y-6">
                  <h3 className="text-base font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800/80 pb-4">
                    Evaluation Output
                  </h3>

                  {simPrediction ? (
                    <div className="space-y-6">
                      <div>
                        <p className="text-sm text-slate-400 font-semibold">Evaluated Target</p>
                        <p className="text-2xl font-mono font-bold text-indigo-400 mt-1">
                          {simPrediction.user}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-400 font-semibold">Score</p>
                        <p className="text-4xl font-extrabold font-mono text-white mt-1">
                          {simPrediction.overall_risk_score}%
                        </p>
                        <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden mt-2.5">
                          <div className={`h-full ${getSeverityStyle(simPrediction.severity).bar}`} style={{ width: `${Math.min(simPrediction.overall_risk_score, 100)}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-slate-400 font-semibold">Threat Level</p>
                        <span className={`inline-block mt-2.5 px-4 py-1.5 rounded-lg text-sm font-bold uppercase border ${getSeverityStyle(simPrediction.severity).badge}`}>
                          {simPrediction.severity}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-slate-500 py-12 space-y-3">
                      <Sliders className="w-10 h-10 text-slate-600 mx-auto" />
                      <p className="text-sm">Select or type user ID to load their baseline, adjust parameters, and click "Analyze Behavior" to evaluate session threat risk.</p>
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

        </main>
      </div>

    </div>
  );
}