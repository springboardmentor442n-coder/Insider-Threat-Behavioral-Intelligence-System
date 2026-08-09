import React, { useState } from 'react';
import { Radar, CheckCircle, XCircle, Play, Brain, Eye, ShieldAlert, Sparkles, Filter, RefreshCw } from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import {
  Spinner, ErrorState, EmptyState, Modal,
  FilterRow, SelectFilter, Pagination
} from '../../components/common';
import { usePaginated, useFetch } from '../../hooks/useFetch';
import { anomalyAPI } from '../../api/client';
import { fmtDT, apiError, ANOMALY_LABELS } from '../../utils/helpers';
import toast from 'react-hot-toast';

const ANOMALY_TYPES = Object.entries(ANOMALY_LABELS).map(([value, label]) => ({ value, label }));

const RISK_SEVERITY_COLORS = {
  critical: '#FF3B5C', // Neon Red
  high: '#FF7C2A',     // Neon Orange
  medium: '#FFC400',   // Neon Yellow
  low: '#00FFA3',      // Neon Green
  info: '#00D9FF'      // Neon Cyan
};

function AnomalyDetailModal({ anomaly, open, onClose, onReviewed }) {
  const [saving, setSaving] = useState(false);

  const review = async (confirmed) => {
    setSaving(true);
    try {
      await anomalyAPI.review(anomaly.id, { is_confirmed: confirmed });
      toast.success(confirmed ? 'Confirmed as true positive' : 'Marked as false positive');
      onReviewed(); 
      onClose();
    } catch (err) { 
      toast.error(apiError(err)); 
    } finally { 
      setSaving(false); 
    }
  };

  if (!anomaly) return null;

  const scoreColor = anomaly.anomaly_score >= 0.7 ? RISK_SEVERITY_COLORS.critical
                   : anomaly.anomaly_score >= 0.4 ? RISK_SEVERITY_COLORS.high
                   : RISK_SEVERITY_COLORS.medium;

  return (
    <Modal open={open} onClose={onClose} title={`Telemetry Audit: Anomaly #${anomaly.id}`} width={550}>
      <div className="flex flex-col gap-5">
        
        {/* Score Ring Section */}
        <div className="text-center py-4 bg-cyber-bg/50 border border-cyber-border/40 rounded-2xl flex flex-col items-center justify-center">
          <div className="relative flex items-center justify-center w-24 h-24 rounded-full border-4 shadow-lg animate-pulse"
            style={{
              borderColor: scoreColor,
              background: `${scoreColor}10`,
              boxShadow: `0 0 15px ${scoreColor}20`
            }}
          >
            <span className="text-3xl font-black font-mono" style={{ color: scoreColor }}>
              {(anomaly.anomaly_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-[10px] font-bold text-cyber-muted uppercase tracking-wider mt-2">
            AI Anomaly Confidence Score
          </div>
        </div>

        {/* Description Panel */}
        <div className="card-purple bg-gradient-to-r from-cyber-card to-cyber-bg border border-cyber-secondary/20 p-4 rounded-xl">
          <div className="text-xs font-bold text-cyber-primary uppercase tracking-wide mb-1">
            {ANOMALY_LABELS[anomaly.anomaly_type] || anomaly.anomaly_type}
          </div>
          <div className="text-[11px] text-gray-300 leading-relaxed italic">
            "{anomaly.description}"
          </div>
        </div>

        {/* Feature Breakdown Table */}
        {anomaly.features && (
          <div className="space-y-2">
            <div className="text-[9px] font-bold text-cyber-muted uppercase tracking-wider flex items-center gap-1">
              <Sparkles size={10} className="text-cyber-accent" /> Associated Feature telemetry
            </div>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1 scrollbar-thin">
              {Object.entries(anomaly.features).map(([k, v]) => (
                <div key={k} className="bg-cyber-card/60 border border-cyber-border/50 rounded-lg p-2 flex flex-col justify-between">
                  <span className="text-[8px] font-semibold text-cyber-dim uppercase tracking-wider truncate">
                    {k.replace(/_/g, ' ')}
                  </span>
                  <span className="font-mono text-xs font-bold text-white mt-1">
                    {typeof v === 'number' ? v.toFixed(3) : String(v)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata Footer */}
        <div className="flex justify-between items-center text-[9px] text-cyber-dim font-mono border-t border-cyber-border/40 pt-3">
          <span>Model: <span className="text-cyber-accent font-bold">{anomaly.model_name || 'IsolationForest'}</span></span>
          <span>Detected At: {fmtDT(anomaly.detected_at)}</span>
        </div>

        {/* Review Action Controls */}
        {anomaly.is_confirmed === null || anomaly.is_confirmed === undefined ? (
          <div className="flex gap-3 mt-2">
            <button
              className="flex-1 btn btn-danger justify-center text-xs py-2"
              onClick={() => review(true)}
              disabled={saving}
            >
              <CheckCircle size={14} /> Confirm Threat (True Positive)
            </button>
            <button
              className="flex-1 btn btn-ghost justify-center text-xs py-2 hover:border-cyber-accent"
              onClick={() => review(false)}
              disabled={saving}
            >
              <XCircle size={14} /> Dismiss Anomaly (False Positive)
            </button>
          </div>
        ) : (
          <div className="text-center py-2.5 rounded-xl font-bold text-xs shadow-inner mt-2 border"
            style={{
              background: anomaly.is_confirmed ? 'rgba(255, 59, 92, 0.08)' : 'rgba(0, 255, 163, 0.08)',
              borderColor: anomaly.is_confirmed ? '#FF3B5C30' : '#00FFA330',
              color: anomaly.is_confirmed ? '#FF3B5C' : '#00FFA3'
            }}
          >
            {anomaly.is_confirmed ? '✓ Confirmed as True Positive Incident' : '✗ Marked as False Positive'}
          </div>
        )}

      </div>
    </Modal>
  );
}

export default function AnomaliesPage() {
  const [selected, setSelected] = useState(null);
  const [typeFilter, setTypeFilter] = useState('');
  const [days, setDays] = useState('7');
  const [empIdDetect, setEmpIdDetect] = useState('');
  const [detecting, setDetecting] = useState(false);
  const [training, setTraining] = useState(false);

  const { data, loading, error, refetch, page, setPage, updateParams } = usePaginated(
    p => anomalyAPI.list(p).then(r => r.data),
    { days: 7 }, 50
  );

  const runDetect = async () => {
    if (!empIdDetect) return toast.error('Enter an employee ID or Code');
    setDetecting(true);
    try {
      await anomalyAPI.detect(empIdDetect);
      toast.success('Behavioral anomaly analysis queued');
      refetch();
    } catch (err) { 
      toast.error(apiError(err)); 
    } finally { 
      setDetecting(false); 
    }
  };

  const trainModel = async () => {
    setTraining(true);
    try {
      await anomalyAPI.train();
      toast.success('Isolation Forest model retraining triggered');
    } catch (err) { 
      toast.error(apiError(err)); 
    } finally { 
      setTraining(false); 
    }
  };

  const scoreColor = (s) =>
    s >= 0.7 ? RISK_SEVERITY_COLORS.critical : s >= 0.4 ? RISK_SEVERITY_COLORS.high : RISK_SEVERITY_COLORS.medium;

  // Compute stat metrics
  const anomaliesList = Array.isArray(data) ? data : [];
  const unreviewedCount = anomaliesList.filter(a => a.is_confirmed === null || a.is_confirmed === undefined).length;
  const confirmedCount = anomaliesList.filter(a => a.is_confirmed === true).length;

  return (
    <AppLayout title="Anomaly Intelligence Panel" subtitle="Continuous unsupervised behavioral anomaly tracking">
      
      {/* Controls & Mini Counters Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        
        {/* Run analysis card */}
        <div className="card lg:col-span-2 flex flex-col justify-between p-4 bg-gradient-to-r from-cyber-card to-cyber-bg border border-cyber-primary/20">
          <div>
            <h3 className="text-[10px] font-bold text-cyber-primary uppercase tracking-wider mb-2">
              Behavioral Scan Engine
            </h3>
            <div className="flex gap-2">
              <input
                className="form-input flex-1"
                placeholder="Enter ID or Code (e.g. EMP001)..."
                value={empIdDetect}
                onChange={e => setEmpIdDetect(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && runDetect()}
              />
              <button
                className="btn btn-primary text-[10px] px-3 font-bold"
                onClick={runDetect}
                disabled={detecting}
              >
                {detecting ? 'Analyzing...' : 'Scan Subject'}
              </button>
            </div>
          </div>
        </div>

        {/* Retrain Model card */}
        <div className="card flex flex-col justify-between p-4 border border-cyber-secondary/20">
          <div>
            <h3 className="text-[10px] font-bold text-cyber-secondary uppercase tracking-wider mb-2">
              Anomaly Calibration
            </h3>
            <button
              className="btn btn-ghost w-full justify-center text-[10px] hover:border-cyber-secondary"
              onClick={trainModel}
              disabled={training}
            >
              <Brain size={12} className="text-cyber-secondary" />
              {training ? 'Recalibrating...' : 'Retrain I-Forest'}
            </button>
          </div>
        </div>

        {/* KPI Counter card */}
        <div className="card flex items-center justify-between p-4 bg-cyber-card/60">
          <div>
            <h3 className="text-[9px] font-bold text-cyber-muted uppercase tracking-wider">Unreviewed Anomalies</h3>
            <div className="text-2xl font-black text-cyber-warning mt-1">{unreviewedCount}</div>
          </div>
          <ShieldAlert size={24} className="text-cyber-warning animate-pulse" />
        </div>

      </div>

      {/* Filter Row with color elements */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between mb-4 bg-cyber-card/30 border border-cyber-border/40 p-3 rounded-2xl">
        <div className="flex flex-wrap gap-2 items-center">
          <div className="flex items-center gap-1 bg-cyber-bg px-2.5 py-1.5 rounded-lg border border-cyber-border text-xs text-cyber-muted">
            <Filter size={11} /> Filters
          </div>
          <SelectFilter
            value={typeFilter}
            onChange={v => { setTypeFilter(v); updateParams({ anomaly_type: v || undefined }); }}
            options={ANOMALY_TYPES}
            placeholder="All Anomaly Categories"
          />
          <SelectFilter
            value={days}
            onChange={v => { setDays(v); updateParams({ days: Number(v) }); }}
            options={[7,14,30,60,90].map(d => ({ value: String(d), label: `Scan limit: ${d} Days` }))}
            placeholder="Scanning Window"
          />
        </div>
        <button
          className="btn btn-ghost text-[10px] px-3 font-semibold flex items-center gap-1"
          onClick={refetch}
        >
          <RefreshCw size={11} /> Refresh list
        </button>
      </div>

      {/* Anomalies Table Card */}
      <div className="card p-0 border border-cyber-border/80">
        {loading ? (
          <div className="py-24"><Spinner /></div>
        ) : error ? (
          <ErrorState message={error} />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Anomaly Severity</th>
                  <th>Detection Category</th>
                  <th>Subject Code</th>
                  <th>Incident Telemetry Summary</th>
                  <th>Model Driver</th>
                  <th>Flagged Time</th>
                  <th>Review Status</th>
                </tr>
              </thead>
              <tbody>
                {anomaliesList.map(a => {
                  const sColor = scoreColor(a.anomaly_score);
                  return (
                    <tr key={a.id} className="cursor-pointer hover:bg-cyber-primary/5 transition-all" onClick={() => setSelected(a)}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-mono font-bold text-[10px] shadow-sm"
                            style={{
                              borderColor: sColor,
                              background: `${sColor}10`,
                              color: sColor
                            }}
                          >
                            {(a.anomaly_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="text-[11px] font-semibold text-white">
                          {ANOMALY_LABELS[a.anomaly_type] || a.anomaly_type}
                        </span>
                      </td>
                      <td>
                        <span className="mono text-[10px] text-cyber-primary font-bold">{a.employee_id}</span>
                      </td>
                      <td className="max-w-xs">
                        <span className="block truncate text-[11px] text-gray-300">
                          {a.description}
                        </span>
                      </td>
                      <td>
                        <span className="mono text-[10px] text-cyber-secondary font-semibold">{a.model_name || 'I-Forest'}</span>
                      </td>
                      <td className="text-[10px] text-gray-400 font-mono">
                        {fmtDT(a.detected_at)}
                      </td>
                      <td>
                        {a.is_confirmed === true && (
                          <span className="badge text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border border-cyber-danger/30"
                            style={{ background: 'rgba(255, 59, 92, 0.1)', color: RISK_SEVERITY_COLORS.critical }}
                          >
                            True Positive
                          </span>
                        )}
                        {a.is_confirmed === false && (
                          <span className="badge text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border border-cyber-accent/30"
                            style={{ background: 'rgba(0, 255, 163, 0.1)', color: RISK_SEVERITY_COLORS.low }}
                          >
                            False Alarm
                          </span>
                        )}
                        {(a.is_confirmed === null || a.is_confirmed === undefined) && (
                          <span className="badge text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border border-cyber-warning/30"
                            style={{ background: 'rgba(255, 196, 0, 0.1)', color: RISK_SEVERITY_COLORS.medium }}
                          >
                            Unreviewed
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {anomaliesList.length === 0 && (
                  <tr>
                    <td colSpan={7}>
                      <EmptyState icon={Radar} message="No anomalous behavior profiles triggered inside current scanning window." />
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <Pagination page={page} setPage={setPage} hasMore={anomaliesList.length === 50} pageSize={50} />}
      </div>

      {/* Slide-out Telemetry Details Modal */}
      <AnomalyDetailModal anomaly={selected} open={!!selected}
        onClose={() => setSelected(null)} onReviewed={refetch} />

    </AppLayout>
  );
}
