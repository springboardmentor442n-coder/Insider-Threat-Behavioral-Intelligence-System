import React, { useState } from 'react';
import {
  Brain, Upload, Play, AlertTriangle, CheckCircle,
  BarChart2, RefreshCw, Cpu, Zap, Activity, Shield,
  Target, Layers, Info, TrendingUp,
} from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import { Spinner } from '../../components/common';
import { useFetch } from '../../hooks/useFetch';
import api from '../../api/client';
import { apiError } from '../../utils/helpers';
import toast from 'react-hot-toast';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from 'recharts';

const RISK_COLOR = {
  'Critical Risk': '#f43f5e',
  'High Risk':     '#f97316',
  'Medium Risk':   '#f59e0b',
  'Low Risk':      '#10b981',
  'Normal':        '#6366f1',
};

const RISK_BG = {
  'Critical Risk': 'rgba(244, 63, 94, 0.1)',
  'High Risk':     'rgba(249, 115, 22, 0.1)',
  'Medium Risk':   'rgba(245, 158, 11, 0.1)',
  'Low Risk':      'rgba(16, 185, 129, 0.1)',
  'Normal':        'rgba(99, 102, 241, 0.1)',
};

const RISK_ICON = {
  'Critical Risk': '🔴',
  'High Risk':     '🟠',
  'Medium Risk':   '🟡',
  'Low Risk':      '🟢',
  'Normal':        '🔵',
};

function StatusBadge({ loaded }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8,
      padding: '6px 14px', borderRadius: 999,
      background: loaded ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
      border: `1px solid ${loaded ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}`,
    }}>
      <div style={{
        width: 8, height: 8, borderRadius: '50%',
        background: loaded ? '#10b981' : '#f43f5e',
        boxShadow: `0 0 8px ${loaded ? '#10b981' : '#f43f5e'}`,
        animation: loaded ? 'pulse-ring 2s infinite' : 'none',
      }} />
      <span style={{
        fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.07em', textTransform: 'uppercase',
        color: loaded ? '#34d399' : '#fca5a5',
      }}>
        {loaded ? 'MODEL ONLINE' : 'NOT LOADED — TRAIN FIRST'}
      </span>
    </div>
  );
}

function PredictionResult({ result }) {
  if (!result) return null;

  const level = result.threat_level || 'Normal';
  const color = RISK_COLOR[level] || '#6366f1';
  const bg = RISK_BG[level] || 'rgba(99,102,241,0.1)';

  // Backend returns confidence as 0-100 (we already handle this in inference.py)
  const confidence = typeof result.confidence === 'number'
    ? (result.confidence > 1 ? result.confidence : result.confidence * 100)
    : 0;
  const threatScore = Math.round(result.threat_score || 0);
  const iforestScore = result.isolation_forest_score?.toFixed(1) || '—';

  // Radar chart data — top 8 features
  const radarData = (result.top_features || []).slice(0, 8).map(item => ({
    feature: item.feature.replace(/_/g, ' ').split(' ').slice(0, 2).join(' ').replace(/\b\w/g, c => c.toUpperCase()),
    weight: Math.min(Math.abs(item.contribution) * 200, 100),
    rawVal: item.value,
  }));

  // Bar chart — class probabilities (always 0–100 range)
  const probData = Object.entries(result.class_probabilities || {}).map(([cls, prob]) => ({
    class: cls,
    probability: Math.round(prob > 1 ? prob : prob * 100),
  })).sort((a, b) => b.probability - a.probability);

  const featureColors = ['#00d4ff', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#3b82f6', '#14b8a6', '#ec4899'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginTop: 18, animation: 'fadeInUp 0.4s ease' }}>

      {/* ── Verdict Panel ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 24px', borderRadius: 16,
        background: bg, border: `1px solid ${color}40`,
        boxShadow: `0 0 30px ${color}12`,
        flexWrap: 'wrap', gap: 16,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 14,
            background: `${color}20`, border: `2px solid ${color}50`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.6rem',
          }}>
            {RISK_ICON[level]}
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 2 }}>
              AI Risk Diagnosis Verdict
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 900, color, lineHeight: 1 }}>
              {level.toUpperCase()}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Deviation: <strong style={{ color: '#fff' }}>{iforestScore}%</strong>
              &nbsp;·&nbsp;
              Prediction: <strong style={{ color }}>{result.xgboost_prediction}</strong>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 20 }}>
          {/* Threat Score */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 900, color, lineHeight: 1 }}>
              {threatScore}
            </div>
            <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
              Threat Score
            </div>
          </div>
          {/* Confidence */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent)', lineHeight: 1 }}>
              {Math.round(confidence)}%
            </div>
            <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
              Confidence
            </div>
          </div>
        </div>
      </div>

      {/* ── Charts Row ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

        {/* Class Probabilities */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            Classification Probabilities
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={probData} layout="vertical" margin={{ left: 10, right: 16 }}>
              <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`}
                tick={{ fill: 'var(--text-muted)', fontSize: 9 }} tickLine={false} axisLine={false} />
              <YAxis type="category" dataKey="class" width={90}
                tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: '#0a0f1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, fontSize: 11 }}
                formatter={v => [`${v}%`, 'Probability']}
              />
              <Bar dataKey="probability" radius={[0, 6, 6, 0]}>
                {probData.map((entry, i) => (
                  <Cell key={i} fill={RISK_COLOR[entry.class] || '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* SHAP Radar */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
            SHAP Positive Contributor Radar
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="feature" tick={{ fill: 'var(--text-muted)', fontSize: 8 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 7 }} />
              <Radar name="SHAP Weight" dataKey="weight" stroke={color} fill={color} fillOpacity={0.2} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Feature Breakdown ── */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <Layers size={13} color="var(--accent)" />
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Feature Contribution Analysis
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
          {(result.top_features || []).map((feat, idx) => {
            const isPositive = feat.contribution >= 0;
            const c = featureColors[idx % featureColors.length];
            const pct = Math.min(Math.abs(feat.contribution) * 200, 100);
            return (
              <div key={idx} style={{
                padding: '10px 14px', borderRadius: 10,
                background: 'rgba(255,255,255,0.025)',
                border: `1px solid ${c}22`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {feat.feature.replace(/_/g, ' ')}
                  </span>
                  <span style={{
                    fontSize: '0.72rem', fontFamily: 'var(--font-mono)', fontWeight: 700,
                    color: isPositive ? '#f43f5e' : '#10b981',
                  }}>
                    {isPositive ? '+' : ''}{(feat.contribution * 100).toFixed(1)}%
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: c, borderRadius: 3, transition: 'width 0.6s ease' }} />
                  </div>
                  <span style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', flexShrink: 0 }}>
                    {feat.value?.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── AI Explanation ── */}
      <div className="card" style={{ border: `1px solid ${color}20` }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <Info size={12} color="var(--accent)" />
              <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                AI Behavioral Analysis
              </span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.7, fontStyle: 'italic' }}>
              "{result.shap_explanation}"
            </p>
          </div>
          <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: 10, border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', marginBottom: 8 }}>
              Incident Response
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-primary)', lineHeight: 1.6, fontWeight: 500 }}>
              {result.recommended_action}
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}

export default function MLPage() {
  const [empId, setEmpId] = useState('');
  const [days, setDays] = useState(30);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [training, setTraining] = useState(false);
  const [uploading, setUploading] = useState(false);

  const { data: status, refetch: refetchStatus } = useFetch(
    () => api.get('/ml/status').then(r => r.data), []
  );

  const runPredict = async () => {
    if (!empId.trim()) return toast.error('Enter an Employee ID or Code');
    setRunning(true);
    setResult(null);
    try {
      const { data } = await api.post(`/ml/predict/${empId.trim()}?days=${days}`);
      setResult(data);
      toast.success(`Prediction generated for ${data.employee_name || empId}`);
      refetchStatus();
    } catch (err) {
      toast.error(apiError(err));
    } finally {
      setRunning(false);
    }
  };

  const triggerTraining = async () => {
    setTraining(true);
    try {
      await api.post(`/ml/train?epochs=50&feature_window=${days}`);
      toast.success('Retraining triggered! This runs in background (30–60s).');
      setTimeout(() => refetchStatus(), 5000);
    } catch (err) {
      toast.error(apiError(err));
    } finally {
      setTraining(false);
    }
  };

  const uploadInsiders = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      await api.post('/ml/upload-insiders', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success('CERT insider labels loaded — training triggered!');
      setTimeout(() => refetchStatus(), 5000);
    } catch (err) {
      toast.error(apiError(err));
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const modelLoaded = status?.model_loaded === true;

  return (
    <AppLayout
      title="ML Behavioral Intelligence Engine"
      subtitle="Standard Random Forest risk classification with SHAP explainability"
    >
      {/* ── Model Status Bar ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 18px', marginBottom: 20,
        background: 'rgba(0,0,0,0.3)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 14,
        flexWrap: 'wrap', gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <StatusBadge loaded={modelLoaded} />
          {status && (
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              {status.status_message || status.architecture}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <div style={{ padding: '5px 12px', borderRadius: 8, background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.15)', fontSize: '0.7rem', color: 'var(--accent)' }}>
            {status?.n_features || 20} Features
          </div>
          <div style={{ padding: '5px 12px', borderRadius: 8, background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.15)', fontSize: '0.7rem', color: '#a78bfa' }}>
            {status?.n_classes || 5} Risk Classes
          </div>
          <div style={{ padding: '5px 12px', borderRadius: 8, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)', fontSize: '0.7rem', color: '#34d399' }}>
            Random Forest
          </div>
        </div>
      </div>

      {/* ── KPI Stats ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
        {[
          { label: 'Engine Status',    value: modelLoaded ? 'ONLINE' : 'OFFLINE', color: modelLoaded ? '#10b981' : '#f43f5e', icon: Brain },
          { label: 'Input Dimensions', value: '20 Features',  color: '#00d4ff', icon: BarChart2 },
          { label: 'Output Targets',   value: '5 Classes',    color: '#f59e0b', icon: Target },
          { label: 'Model Pipeline',   value: 'Random Forest',color: '#8b5cf6', icon: Cpu },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="stat-card" style={{ '--card-accent': color }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${color}28` }}>
                <Icon size={14} color={color} />
              </div>
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color, marginBottom: 2 }}>{value}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* ── Risk Classes Legend ── */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
          Risk Classification Targets
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {Object.entries(RISK_COLOR).map(([cls, color]) => (
            <div key={cls} style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '6px 14px', borderRadius: 999,
              background: `${color}10`, border: `1px solid ${color}30`, color,
            }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, boxShadow: `0 0 6px ${color}` }} />
              <span style={{ fontSize: '0.75rem', fontWeight: 700 }}>{cls}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Control Console ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 20 }}>

        {/* Predict Panel */}
        <div className="card" style={{ border: '1px solid rgba(0,212,255,0.15)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Zap size={14} color="var(--accent)" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Behavioral Risk Inference
            </span>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: 160 }}>
              <label className="form-label">Subject Code / Database ID</label>
              <input
                className="form-input"
                placeholder="e.g. EMP001 or numeric ID..."
                value={empId}
                onChange={e => setEmpId(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && runPredict()}
              />
            </div>
            <div style={{ minWidth: 130 }}>
              <label className="form-label">Feature Window</label>
              <select
                className="form-input"
                value={days}
                onChange={e => setDays(Number(e.target.value))}
              >
                {[7, 14, 30, 60, 90].map(d => <option key={d} value={d}>{d} days</option>)}
              </select>
            </div>
            <button
              className="btn btn-primary"
              onClick={runPredict}
              disabled={running}
              style={{ padding: '10px 20px', fontSize: '0.82rem', whiteSpace: 'nowrap' }}
            >
              <Play size={13} /> {running ? 'Running…' : 'Run Predict'}
            </button>
          </div>

          {!modelLoaded && (
            <div className="alert-banner alert-medium" style={{ marginTop: 12 }}>
              <AlertTriangle size={14} />
              <span>Model not trained yet. Click <strong>Retrain Calibration</strong> to train the hybrid ML engine first, then run predictions.</span>
            </div>
          )}
        </div>

        {/* Calibration Console */}
        <div className="card" style={{ border: '1px solid rgba(139,92,246,0.15)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Brain size={14} color="#8b5cf6" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#8b5cf6', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Model Calibration Console
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button
              className="btn"
              onClick={triggerTraining}
              disabled={training}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                color: '#fff', justifyContent: 'center', fontSize: '0.8rem',
                boxShadow: training ? 'none' : '0 4px 15px rgba(139,92,246,0.3)',
              }}
            >
              {training ? <RefreshCw size={13} style={{ animation: 'spin-slow 1s linear infinite' }} /> : <Brain size={13} />}
              {training ? 'Training…' : 'Retrain Calibration'}
            </button>
            <label className="btn btn-ghost" style={{ justifyContent: 'center', cursor: 'pointer', fontSize: '0.8rem' }}>
              <Upload size={13} />
              {uploading ? 'Processing…' : 'Upload insiders.csv'}
              <input type="file" accept=".csv" onChange={uploadInsiders} hidden disabled={uploading} />
            </label>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 2 }}>
              Upload CERT r4.2 answers CSV to provide labeled insider threat ground truth for supervised training.
            </div>
          </div>
        </div>
      </div>

      {/* ── Results Panel ── */}
      {running && (
        <div style={{ textAlign: 'center', padding: '50px 0', background: 'rgba(0,0,0,0.2)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.05)' }}>
          <Spinner />
          <p style={{ fontSize: '0.82rem', color: 'var(--accent)', fontFamily: 'var(--font-mono)', marginTop: 12, animation: 'blink 1.5s infinite' }}>
            Extracting behavioral features → Running hybrid inference…
          </p>
        </div>
      )}
      {result && <PredictionResult result={result} />}

    </AppLayout>
  );
}
