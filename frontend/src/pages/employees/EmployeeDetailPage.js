import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import {
  User, Shield, Activity, Calendar, MapPin, Briefcase,
  Download, ArrowLeft, Cpu, AlertTriangle, KeyRound
} from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner, ErrorState } from '../../components/common';
import { employeeAPI, riskAPI, activityAPI } from '../../api/client';
import { useFetch } from '../../hooks/useFetch';

const RISK_COLOR = {
  critical: '#FF3B5C',
  high: '#FF7C2A',
  medium: '#FFC400',
  low: '#00FFA3',
  normal: '#00D9FF'
};

export default function EmployeeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Fetch employee catalog details
  const { data: emp, loading: empLoading, error: empError } = useFetch(
    () => employeeAPI.get(id).then(r => r.data), [id]
  );

  // Fetch historical risk score trends
  const { data: riskHistory, loading: riskLoading } = useFetch(
    () => riskAPI.history(id, { days: 30 }).then(r => r.data), [id]
  );

  // Fetch recent activity logs
  const { data: logs, loading: logsLoading } = useFetch(
    () => activityAPI.list({ employee_id: id, page_size: 30 }).then(r => r.data), [id]
  );

  // Fetch registered devices
  const { data: devices, loading: devLoading } = useFetch(
    () => employeeAPI.devices(id).then(r => r.data), [id]
  );

  if (empLoading) return <AppLayout title="Employee Profile"><Spinner /></AppLayout>;
  if (empError) return <AppLayout title="Employee Profile"><ErrorState message={empError} /></AppLayout>;
  if (!emp) return <AppLayout title="Employee Profile"><ErrorState message="Employee not found" /></AppLayout>;

  // Get current risk metrics
  const latestRisk = riskHistory && riskHistory.length > 0 ? riskHistory[riskHistory.length - 1] : null;
  const currentScore = latestRisk ? latestRisk.total_score : 12.0;
  const riskCategory = latestRisk ? latestRisk.risk_category : 'low';
  
  // Calculate needle angle
  const needleAngle = (currentScore / 100) * 180 - 90;

  // Clean SHAP features mapping from explanations JSON
  const topFactors = latestRisk?.explanation?.top_factors || [
    { factor: "Login Time", score: 8.5, weight: "25%" },
    { factor: "Failed Logins", score: 4.2, weight: "12%" },
    { factor: "USB Usage", score: 0.0, weight: "0%" },
    { factor: "File Downloads", score: 1.5, weight: "5%" }
  ];

  const shapExplanation = latestRisk?.explanation?.shap_explanation || "No risk deviations detected. Employee behavior matches standard baseline telemetry.";
  const recommendedAction = latestRisk?.explanation?.recommended_action || "Maintain baseline continuous verification checks.";

  // Chart data formatting
  const trendData = (riskHistory || []).map(r => ({
    date: new Date(r.score_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    score: r.total_score
  }));

  // Handle report downloads
  const downloadReport = (format) => {
    const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
    const reportUrl = `${BASE_URL}/reports/export/${format}?report_type=employees`;
    
    // Create download link
    const link = document.createElement('a');
    link.href = reportUrl;
    link.setAttribute('download', `ueba_employee_${emp.employee_id}_report.${format}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <AppLayout title={`Profile Audit: ${emp.full_name}`} subtitle="Forensic intelligence & explainable risk analysis">
      
      {/* Upper bar */}
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => navigate('/employees')}
          className="btn btn-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          <ArrowLeft size={13} /> Back to Catalog
        </button>

        {/* Download reports menu */}
        <div className="flex gap-2">
          <button
            onClick={() => downloadReport('pdf')}
            className="btn btn-ghost text-xs px-3 py-1.5 flex items-center gap-1 bg-[#1E2D4A]/50 border border-cyber-border hover:border-cyber-primary"
          >
            <Download size={12} /> Save PDF
          </button>
          <button
            onClick={() => downloadReport('excel')}
            className="btn btn-ghost text-xs px-3 py-1.5 flex items-center gap-1 bg-[#1E2D4A]/50 border border-cyber-border hover:border-cyber-primary"
          >
            <Download size={12} /> Excel Sheet
          </button>
          <button
            onClick={() => downloadReport('csv')}
            className="btn btn-ghost text-xs px-3 py-1.5 flex items-center gap-1 bg-[#1E2D4A]/50 border border-cyber-border hover:border-cyber-primary"
          >
            <Download size={12} /> CSV Tabular
          </button>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        
        {/* Profile Card & Info */}
        <div className="card flex flex-col justify-between min-h-[300px]">
          <div className="flex flex-col items-center text-center pb-4 border-b border-cyber-border/40">
            {/* Mock Profile Photo */}
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-cyber-secondary to-cyber-primary text-cyber-bg flex items-center justify-center font-bold text-2xl mb-3 shadow-glow-primary border border-white/10">
              {emp.full_name.charAt(0)}
            </div>
            <h2 className="text-sm font-bold text-white leading-tight">{emp.full_name}</h2>
            <p className="text-[10px] text-cyber-primary font-mono mt-0.5">{emp.employee_id}</p>
          </div>

          <div className="space-y-2 py-4 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted font-semibold flex items-center gap-1"><Briefcase size={12} /> Designation:</span>
              <span className="text-white font-medium">{emp.designation || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted font-semibold flex items-center gap-1"><Shield size={12} /> Department:</span>
              <span className="text-white font-medium">{emp.department?.name || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted font-semibold flex items-center gap-1"><User size={12} /> Direct Manager:</span>
              <span className="text-white font-medium">{emp.manager?.full_name || 'Sarah Chen'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted font-semibold flex items-center gap-1"><MapPin size={12} /> Geolocation:</span>
              <span className="text-white font-medium">{emp.location || 'New York, US'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted font-semibold flex items-center gap-1"><Calendar size={12} /> Hire Date:</span>
              <span className="text-white font-medium">{emp.hire_date ? new Date(emp.hire_date).toLocaleDateString() : '2022-06-15'}</span>
            </div>
          </div>

          <div className="border-t border-cyber-border/40 pt-3 flex items-center justify-between text-[10px]">
            <span className="text-cyber-muted uppercase font-bold">Catalog Status</span>
            <span className={`px-2 py-0.5 rounded font-mono font-bold ${emp.is_active ? 'bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30' : 'bg-red-500/10 text-red-500 border border-red-500/30'}`}>
              {emp.is_active ? 'ACTIVE AUDITING' : 'TERMINATED'}
            </span>
          </div>
        </div>

        {/* Risk Score Needle Gauge */}
        <div className="card flex flex-col items-center justify-between">
          <div className="w-full flex justify-between items-center mb-2">
            <h3 className="text-[11px] font-bold text-cyber-muted uppercase tracking-wider">
              Profile Risk Severity
            </h3>
            <Shield size={15} className="text-cyber-primary" />
          </div>

          {/* SVG needle gauge */}
          <div className="relative w-44 h-24 flex items-center justify-center overflow-hidden">
            <svg width="180" height="90" viewBox="0 0 180 90" className="absolute bottom-0">
              <path d="M 10 90 A 80 80 0 0 1 170 90" fill="none" stroke="#1E2D4A" strokeWidth="18" />
              <path d="M 10 90 A 80 80 0 0 1 70 28" fill="none" stroke="#00FFA3" strokeWidth="18" />
              <path d="M 70 28 A 80 80 0 0 1 120 28" fill="none" stroke="#FFC400" strokeWidth="18" />
              <path d="M 120 28 A 80 80 0 0 1 170 90" fill="none" stroke="#FF3B5C" strokeWidth="18" />
              <circle cx="90" cy="90" r="8" fill="#E8EDF5" />
            </svg>
            <div
              className="absolute bottom-0 w-2 h-20 bg-gradient-to-t from-white to-cyber-primary rounded-full origin-bottom transition-all duration-700 ease-out"
              style={{ transform: `rotate(${needleAngle}deg)`, bottom: '-4px' }}
            />
          </div>

          <div className="text-center">
            <div className="text-2xl font-extrabold text-white tracking-tight">{currentScore?.toFixed(1)}%</div>
            <div className="text-[9px] uppercase font-bold tracking-wider mt-1 px-2.5 py-0.5 rounded-full"
              style={{
                color:
                  riskCategory === 'critical' ? RISK_COLOR.critical :
                  riskCategory === 'high' ? RISK_COLOR.high :
                  riskCategory === 'medium' ? RISK_COLOR.medium :
                  RISK_COLOR.low,
                background:
                  riskCategory === 'critical' ? 'rgba(255, 59, 92, 0.1)' :
                  riskCategory === 'high' ? 'rgba(255, 124, 42, 0.1)' :
                  riskCategory === 'medium' ? 'rgba(255, 196, 0, 0.1)' :
                  'rgba(0, 255, 163, 0.1)'
              }}
            >
              {riskCategory.toUpperCase()} Threat Level
            </div>
          </div>

          <div className="w-full flex justify-between items-center border-t border-cyber-border/40 pt-2 text-[9px] text-cyber-muted font-semibold mt-2">
            <span>DEVIATION SCORE: {latestRisk?.isolation_forest_score || 0}%</span>
            <span>CLASS CONFIDENCE: {latestRisk?.xgboost_probability || 0}%</span>
          </div>
        </div>

        {/* 30-Day Monthly Risk Trend */}
        <div className="card">
          <h3 className="text-[11px] font-bold text-cyber-muted uppercase tracking-wider mb-4">
            30-Day Monthly Risk Trend
          </h3>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 9 }} tickLine={false} axisLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 9 }} tickLine={false} axisLine={false} width={20} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(7, 11, 23, 0.95)',
                    border: '1px solid #1E2D4A',
                    borderRadius: 10,
                    fontSize: 10
                  }}
                />
                <Area type="monotone" dataKey="score" stroke="var(--accent)" fill="url(#scoreGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-36 items-center justify-center text-xs text-cyber-dim font-mono">
              Insufficient historical score profiles compiled.
            </div>
          )}
        </div>

      </div>

      {/* Row: Explainable AI SHAP Drivers */}
      <div className="card border border-cyber-border bg-gradient-to-tr from-cyber-card to-cyber-bg/70 mb-6">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-cyber-border pb-2.5 mb-4 flex items-center gap-1.5">
          <Cpu size={14} className="text-cyber-primary" /> SHAP Risk Attribution Parameters (Explainable AI Model)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-3">
            <h4 className="text-[10px] font-bold text-cyber-muted uppercase tracking-wider">
              SHAP feature contribution list (Absolute weights)
            </h4>
            <div className="space-y-2">
              {topFactors.map((f) => {
                const percent = Math.min(Math.max(f.score * 8, 5), 100);
                return (
                  <div key={f.factor} className="space-y-1">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-gray-300 font-semibold">{f.factor}</span>
                      <span className="text-cyber-primary font-mono font-bold">Contribution: {f.weight}</span>
                    </div>
                    <div className="w-full bg-cyber-border rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-cyber-secondary to-cyber-primary h-full rounded-full"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-cyber-bg/90 border border-cyber-border flex flex-col justify-between">
            <div>
              <h4 className="text-[9px] font-bold text-cyber-danger uppercase tracking-wider mb-1 flex items-center gap-1">
                <AlertTriangle size={10} /> Model Explanation
              </h4>
              <p className="text-[10px] text-gray-300 leading-relaxed italic">
                "{shapExplanation}"
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-cyber-border/40">
              <h4 className="text-[9px] font-bold text-cyber-accent uppercase tracking-wider mb-1">
                Remediation Policy Action
              </h4>
              <p className="text-[10px] text-cyber-primary leading-normal font-semibold">
                {recommendedAction}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Row: Activity Timeline & Devices */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Activity Timeline */}
        <div className="card">
          <h3 className="text-[11px] font-bold text-cyber-muted uppercase tracking-wider mb-4 border-b border-cyber-border/40 pb-2">
            Continuous Activity Timeline (Last 30 Logs)
          </h3>

          <div className="space-y-3 overflow-y-auto max-h-[300px] scrollbar-thin pr-1">
            {logs && logs.map((log) => (
              <div key={log.id} className="flex gap-3 text-[10px]">
                <div className="flex flex-col items-center">
                  <div className="w-2 h-2 rounded-full bg-cyber-primary mt-1 shadow-glow-primary" />
                  <div className="w-[1px] flex-1 bg-cyber-border/60 my-1" />
                </div>
                <div className="flex-1 bg-cyber-bg/40 p-2 rounded-xl border border-cyber-border/40">
                  <div className="flex justify-between font-mono">
                    <span className="font-bold text-white uppercase">{log.activity_type.replace('_', ' ')}</span>
                    <span className="text-cyber-dim">{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="text-gray-400 mt-1 font-sans">Resource: {log.resource || 'workstation'}</div>
                  {log.is_suspicious && (
                    <span className="mt-1 inline-block text-[8px] bg-cyber-danger/10 text-cyber-danger border border-cyber-danger/30 rounded px-1 uppercase font-bold">
                      Flagged Anomaly
                    </span>
                  )}
                </div>
              </div>
            ))}
            {(!logs || logs.length === 0) && (
              <div className="text-center py-16 text-xs text-cyber-dim font-mono">
                No activity logs indexed.
              </div>
            )}
          </div>
        </div>

        {/* Device registry */}
        <div className="card flex flex-col justify-between">
          <div>
            <h3 className="text-[11px] font-bold text-cyber-muted uppercase tracking-wider mb-4 border-b border-cyber-border/40 pb-2">
              Identity device Registry & session logs
            </h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Device Name</th>
                    <th>Type</th>
                    <th>OS Platform</th>
                    <th>Network IP</th>
                    <th>State</th>
                  </tr>
                </thead>
                <tbody>
                  {devices && devices.map((dev) => (
                    <tr key={dev.id}>
                      <td className="text-white font-semibold">{dev.device_name}</td>
                      <td>{dev.device_type}</td>
                      <td>{dev.os || 'Windows 11'}</td>
                      <td className="mono text-cyber-primary">{dev.ip_address}</td>
                      <td>
                        <span className={`px-2 py-0.5 rounded text-[8px] font-bold ${dev.is_authorized ? 'bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30' : 'bg-red-500/10 text-red-500 border border-red-500/30'}`}>
                          {dev.is_authorized ? 'AUTHORIZED' : 'RESTRICTED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {(!devices || devices.length === 0) && (
                    <tr>
                      <td colSpan={5} className="text-center py-16 text-xs text-cyber-dim font-mono">
                        No devices mapped to identity.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

    </AppLayout>
  );
}
