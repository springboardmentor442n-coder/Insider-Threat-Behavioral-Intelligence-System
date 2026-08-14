/**
 * ============================================================
 * Employee Evaluation Page
 * Route: /employee-evaluation
 *
 * Three tabs:
 *  1. Evaluate New Employee   — 22-feature form + live inference
 *  2. Newly Evaluated         — session store table + detail drawer
 *  3. Existing vs New         — comparison dashboard + ranking
 * ============================================================
 */

import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  UserPlus,
  Users,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Trash2,
  RotateCcw,
  Shield,
  Activity,
  Cpu,
  Globe,
  Mail,
  Clock,
  HardDrive,
  Brain,
  ArrowUpDown,
  TrendingUp,
  X,
  Info,
  Sparkles,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
} from "recharts";
import employeeEvaluationService from "../../services/api/employeeEvaluationService";
import { useAuth } from "../../providers/AuthProvider";

// ============================================================
// CANONICAL FEATURE SCHEMA (22 features, 5 categories)
// ============================================================

const FEATURE_SCHEMA = [
  {
    category: "Volume & Access",
    icon: Activity,
    color: "#06b6d4",
    fields: [
      { name: "total_events", label: "Total Events", min: 0, max: 1000000, step: 1, default: 800 },
      { name: "active_days", label: "Active Days", min: 1, max: 1000, step: 1, default: 180 },
      { name: "unique_pcs", label: "Unique PCs Used", min: 1, max: 1000, step: 1, default: 2 },
      { name: "unique_sources", label: "Unique Sources", min: 1, max: 100, step: 1, default: 3 },
    ],
  },
  {
    category: "Temporal Activity",
    icon: Clock,
    color: "#8b5cf6",
    fields: [
      { name: "total_logins", label: "Total Logins", min: 0, max: 50000, step: 1, default: 300 },
      { name: "midnight_activity", label: "Midnight Activity", min: 0, max: 50000, step: 1, default: 0 },
      { name: "after_hours_activity", label: "After-Hours Activity", min: 0, max: 50000, step: 1, default: 20 },
      { name: "weekend_activity", label: "Weekend Activity", min: 0, max: 50000, step: 1, default: 10 },
      { name: "average_hour", label: "Average Activity Hour (0–24)", min: 0, max: 24, step: 0.1, default: 10 },
      { name: "earliest_hour", label: "Earliest Activity Hour", min: 0, max: 24, step: 0.1, default: 8 },
      { name: "latest_hour", label: "Latest Activity Hour", min: 0, max: 24, step: 0.1, default: 18 },
    ],
  },
  {
    category: "Device / USB Activity",
    icon: HardDrive,
    color: "#f59e0b",
    fields: [
      { name: "device_events", label: "USB Device Connects", min: 0, max: 50000, step: 1, default: 0 },
      { name: "file_events", label: "File Copy Events", min: 0, max: 50000, step: 1, default: 0 },
      { name: "unique_files", label: "Unique File Copies", min: 0, max: 50000, step: 1, default: 0 },
    ],
  },
  {
    category: "Web & Email Activity",
    icon: Globe,
    color: "#10b981",
    fields: [
      { name: "emails_sent", label: "Emails Sent", min: 0, max: 50000, step: 1, default: 50 },
      { name: "web_events", label: "Web HTTP Requests", min: 0, max: 500000, step: 1, default: 500 },
      { name: "unique_urls", label: "Unique URLs Visited", min: 0, max: 50000, step: 1, default: 100 },
    ],
  },
  {
    category: "Psychometrics",
    icon: Brain,
    color: "#ec4899",
    fields: [
      { name: "openness", label: "Openness Score (0–100)", min: 0, max: 100, step: 0.1, default: 50 },
      { name: "conscientiousness", label: "Conscientiousness (0–100)", min: 0, max: 100, step: 0.1, default: 50 },
      { name: "extraversion", label: "Extraversion (0–100)", min: 0, max: 100, step: 0.1, default: 50 },
      { name: "agreeableness", label: "Agreeableness (0–100)", min: 0, max: 100, step: 0.1, default: 50 },
      { name: "neuroticism", label: "Neuroticism (0–100)", min: 0, max: 100, step: 0.1, default: 50 },
    ],
  },
];

const ALL_FIELDS = FEATURE_SCHEMA.flatMap((c) => c.fields);

// ============================================================
// DEMO PRESETS  — clearly labelled as Demonstration / Test Vectors
// ============================================================

const PRESETS = [
  {
    label: "Normal Employee",
    description: "Low-risk baseline pattern",
    values: {
      total_events: 800, active_days: 200, unique_pcs: 1, unique_sources: 2,
      total_logins: 250, midnight_activity: 0, after_hours_activity: 5,
      weekend_activity: 2, average_hour: 10.5, earliest_hour: 8.0, latest_hour: 17.0,
      device_events: 0, file_events: 0, unique_files: 0,
      emails_sent: 40, web_events: 400, unique_urls: 80,
      openness: 55, conscientiousness: 70, extraversion: 50,
      agreeableness: 65, neuroticism: 30,
    },
  },
  {
    label: "High USB Activity",
    description: "Excessive USB / file copy pattern",
    values: {
      total_events: 4500, active_days: 180, unique_pcs: 3, unique_sources: 4,
      total_logins: 600, midnight_activity: 120, after_hours_activity: 340,
      weekend_activity: 200, average_hour: 14.2, earliest_hour: 6.0, latest_hour: 23.0,
      device_events: 850, file_events: 1200, unique_files: 980,
      emails_sent: 250, web_events: 3200, unique_urls: 1800,
      openness: 80, conscientiousness: 25, extraversion: 60,
      agreeableness: 30, neuroticism: 75,
    },
  },
  {
    label: "Extreme Threat (AJF0370-class)",
    description: "Maximum-risk demonstration vector",
    values: {
      total_events: 45000, active_days: 500, unique_pcs: 18, unique_sources: 22,
      total_logins: 8500, midnight_activity: 3200, after_hours_activity: 6800,
      weekend_activity: 4500, average_hour: 1.8, earliest_hour: 0.1, latest_hour: 23.9,
      device_events: 4200, file_events: 8900, unique_files: 7600,
      emails_sent: 3800, web_events: 95000, unique_urls: 42000,
      openness: 95, conscientiousness: 10, extraversion: 85,
      agreeableness: 5, neuroticism: 95,
    },
  },
];

// ============================================================
// UTILITY HELPERS
// ============================================================

const buildDefaultFeatures = () =>
  Object.fromEntries(ALL_FIELDS.map((f) => [f.name, f.default]));

const RISK_CONFIG = {
  LOW: { color: "#22c55e", bg: "rgba(34,197,94,0.12)", border: "rgba(34,197,94,0.4)", label: "LOW" },
  MEDIUM: { color: "#f59e0b", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.4)", label: "MEDIUM" },
  HIGH: { color: "#f97316", bg: "rgba(249,115,22,0.12)", border: "rgba(249,115,22,0.4)", label: "HIGH" },
  CRITICAL: { color: "#ef4444", bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.4)", label: "CRITICAL" },
};

function getRisk(level) {
  const key = (level || "LOW").toString().toUpperCase();
  return RISK_CONFIG[key] || RISK_CONFIG.LOW;
}

function ThreatBadge({ status }) {
  if (status === "POTENTIAL INSIDER THREAT") {
    return (
      <span style={{ background: "rgba(239,68,68,0.18)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.4)" }}
        className="px-2 py-0.5 rounded-full text-xs font-bold tracking-wide whitespace-nowrap">
        ⚠ POTENTIAL INSIDER THREAT
      </span>
    );
  }
  if (status === "REQUIRES MONITORING") {
    return (
      <span style={{ background: "rgba(245,158,11,0.18)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.4)" }}
        className="px-2 py-0.5 rounded-full text-xs font-bold tracking-wide whitespace-nowrap">
        ◈ REQUIRES MONITORING
      </span>
    );
  }
  return (
    <span style={{ background: "rgba(34,197,94,0.18)", color: "#22c55e", border: "1px solid rgba(34,197,94,0.4)" }}
      className="px-2 py-0.5 rounded-full text-xs font-bold tracking-wide whitespace-nowrap">
      ✓ LOW RISK
    </span>
  );
}

function SourceBadge({ source }) {
  if (source === "NEW_EVALUATION") {
    return (
      <span style={{ background: "rgba(245,158,11,0.18)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.4)" }}
        className="px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide whitespace-nowrap">
        NEW EVALUATION
      </span>
    );
  }
  return (
    <span style={{ background: "rgba(148,163,184,0.12)", color: "#94a3b8", border: "1px solid rgba(148,163,184,0.25)" }}
      className="px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide whitespace-nowrap">
      CERT R4.2
    </span>
  );
}

function RiskBadge({ level }) {
  const cfg = getRisk(level);
  return (
    <span style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}
      className="px-2 py-0.5 rounded-full text-xs font-bold tracking-wide whitespace-nowrap">
      {cfg.label}
    </span>
  );
}

function Stat({ label, value, sub, color }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-lg font-bold" style={{ color: color || "#f1f5f9" }}>{value}</span>
      {sub && <span className="text-xs text-slate-500">{sub}</span>}
    </div>
  );
}

// ============================================================
// GLASS CARD
// ============================================================
function Card({ children, className = "", style = {} }) {
  return (
    <div
      className={`rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm ${className}`}
      style={style}
    >
      {children}
    </div>
  );
}

// ============================================================
// RESULT PANEL — shown after evaluation
// ============================================================
function ResultPanel({ result, onSave, saving }) {
  const [expanded, setExpanded] = useState(false);

  if (!result) return null;

  const risk = getRisk(result.risk_level);
  const emp = result.employee || {};
  const layer2 = result.layer2_verification || {};
  const modelResults = result.model_results || [];

  return (
    <Card className="p-5 mt-5" style={{ border: `1px solid ${risk.border}`, background: risk.bg }}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield size={18} style={{ color: risk.color }} />
            <h3 className="text-base font-bold text-slate-100">
              Evaluation Result — {emp.employee_id || "N/A"}
            </h3>
          </div>
          <p className="text-xs text-slate-400">{emp.employee_name} · {emp.department} · {emp.role}</p>
        </div>
        <div className="flex items-center gap-2">
          <ThreatBadge status={result.threat_status} />
          <RiskBadge level={result.risk_level} />
        </div>
      </div>

      {/* Core metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
        <div className="rounded-lg p-3 bg-white/5 border border-white/10 text-center">
          <div className="text-3xl font-black mb-1" style={{ color: risk.color }}>
            {result.risk_score?.toFixed(1)}
          </div>
          <div className="text-xs text-slate-400">Risk Score</div>
        </div>
        <div className="rounded-lg p-3 bg-white/5 border border-white/10 text-center">
          <div className="text-2xl font-black text-cyan-400 mb-1">
            {result.models_triggered}/{result.models_evaluated || 7}
          </div>
          <div className="text-xs text-slate-400">Models Triggered</div>
        </div>
        <div className="rounded-lg p-3 bg-white/5 border border-white/10 text-center">
          <div className="text-2xl font-black text-violet-400 mb-1">
            {result.consensus_percentage?.toFixed(1)}%
          </div>
          <div className="text-xs text-slate-400">Consensus</div>
        </div>
        <div className="rounded-lg p-3 bg-white/5 border border-white/10 text-center">
          <div className="text-sm font-bold mb-1"
            style={{ color: layer2.supported_by_behavioral_evidence ? "#22c55e" : "#94a3b8" }}>
            {layer2.supported_by_behavioral_evidence ? "✓ Supported" : "– Not Supported"}
          </div>
          <div className="text-xs text-slate-400">CERT Layer 2</div>
        </div>
      </div>

      {/* Model grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 mb-4">
        {modelResults.map((m) => (
          <div key={m.model}
            className="rounded-lg px-3 py-2 border text-xs font-medium"
            style={{
              background: m.status === "suspicious" ? "rgba(239,68,68,0.12)" : "rgba(34,197,94,0.08)",
              borderColor: m.status === "suspicious" ? "rgba(239,68,68,0.35)" : "rgba(34,197,94,0.25)",
              color: m.status === "suspicious" ? "#f87171" : "#86efac",
            }}>
            {m.status === "suspicious" ? "⚠" : "✓"}{" "}
            {(m.model || m.model_name || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            {m.inference_status === "not_directly_inferable" && (
              <span className="block text-slate-500 text-[10px] mt-0.5">not directly inferable</span>
            )}
          </div>
        ))}
      </div>

      {/* Layer 2 vectors */}
      {(layer2.anomalous_vectors || []).length > 0 && (
        <div className="mb-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/25">
          <p className="text-xs font-semibold text-amber-400 mb-2">
            CERT Layer 2 — Anomalous Behavioral Vectors ({layer2.anomalous_vectors_count}/{layer2.total_vectors_tested})
          </p>
          {layer2.anomalous_vectors.map((v) => (
            <div key={v} className="flex items-center gap-1.5 text-xs text-amber-300 mb-1">
              <AlertTriangle size={11} /> {v}
            </div>
          ))}
        </div>
      )}

      {/* Behavioral evidence */}
      {result.behavioral_evidence?.length > 0 && (
        <div className="mb-4">
          <button
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
            onClick={() => setExpanded((e) => !e)}
          >
            {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            {expanded ? "Hide" : "Show"} behavioral evidence
          </button>
          {expanded && (
            <ul className="mt-2 space-y-1">
              {result.behavioral_evidence.map((ev, i) => (
                <li key={i} className="text-xs text-slate-400 flex items-start gap-1.5">
                  <Info size={11} className="mt-0.5 shrink-0 text-cyan-500" /> {ev}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Disclaimer */}
      {layer2.disclaimer && (
        <p className="text-[10px] text-slate-500 italic mb-4 border-t border-white/10 pt-3">
          {layer2.disclaimer}
        </p>
      )}

      {/* Save button */}
      <button
        onClick={onSave}
        disabled={saving}
        className="w-full py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2"
        style={{
          background: saving ? "rgba(255,255,255,0.05)" : "linear-gradient(135deg, #06b6d4, #8b5cf6)",
          color: saving ? "#64748b" : "#fff",
          cursor: saving ? "not-allowed" : "pointer",
        }}
      >
        {saving ? <RefreshCw size={14} className="animate-spin" /> : <CheckCircle size={14} />}
        {saving ? "Saving…" : "Save Evaluation to Session Store"}
      </button>
    </Card>
  );
}

// ============================================================
// DETAIL DRAWER — individual employee details + percentile
// ============================================================
function DetailDrawer({ evaluation, onClose }) {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const empId = evaluation?.employee?.employee_id || evaluation?.employee_id || "";

  useEffect(() => {
    if (!empId) return;
    setLoading(true);
    setError(null);
    employeeEvaluationService
      .getIndividualComparison(empId)
      .then(setComparison)
      .catch((e) => setError(e?.response?.data?.detail || "Failed to load comparison."))
      .finally(() => setLoading(false));
  }, [empId]);

  if (!evaluation) return null;

  const risk = getRisk(evaluation.risk_level);
  const layer2 = evaluation.layer2_verification || {};
  const emp = evaluation.employee || {};

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-end"
      style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
      onClick={onClose}
    >
      <div
        className="relative h-full w-full max-w-2xl bg-slate-950 border-l border-white/10 overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer header */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-slate-950 border-b border-white/10">
          <div>
            <h2 className="text-base font-bold text-slate-100">{emp.employee_name || empId}</h2>
            <p className="text-xs text-slate-400">{emp.department} · {emp.role}</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to={`/explainability?employee=${empId}`}
              className="
                flex
                items-center
                gap-1.5
                rounded-xl
                border
                border-purple-500/30
                bg-purple-500/10
                px-3
                py-1.5
                text-xs
                font-semibold
                text-purple-400
                transition
                hover:border-purple-500/50
                hover:bg-purple-500/20
              "
            >
              <Sparkles className="h-4 w-4" />
              Explainability
            </Link>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-100 transition-colors p-1">
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Risk overview */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: "Risk Score", value: evaluation.risk_score?.toFixed(1), color: risk.color },
              { label: "Risk Level", value: evaluation.risk_level, color: risk.color },
              { label: "Models", value: `${evaluation.models_triggered}/${evaluation.models_evaluated || 7}`, color: "#06b6d4" },
              { label: "Consensus", value: `${evaluation.consensus_percentage?.toFixed(1)}%`, color: "#8b5cf6" },
            ].map((s) => (
              <div key={s.label} className="rounded-lg p-3 bg-white/5 border border-white/10 text-center">
                <div className="text-lg font-black mb-0.5" style={{ color: s.color }}>{s.value}</div>
                <div className="text-xs text-slate-400">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <ThreatBadge status={evaluation.threat_status} />
            <SourceBadge source="NEW_EVALUATION" />
          </div>

          {/* Layer 2 */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
              CERT Layer 2 Behavioral Verification
            </h3>
            <div className="rounded-lg p-3 border"
              style={{
                background: layer2.supported_by_behavioral_evidence ? "rgba(34,197,94,0.08)" : "rgba(148,163,184,0.08)",
                borderColor: layer2.supported_by_behavioral_evidence ? "rgba(34,197,94,0.25)" : "rgba(148,163,184,0.2)",
              }}>
              <p className="text-sm font-semibold mb-2"
                style={{ color: layer2.supported_by_behavioral_evidence ? "#22c55e" : "#94a3b8" }}>
                {layer2.validation_status || "—"}
              </p>
              <p className="text-xs text-slate-500">
                {layer2.anomalous_vectors_count || 0} of {layer2.total_vectors_tested || 6} behavioral vectors anomalous
              </p>
              {(layer2.anomalous_vectors || []).map((v) => (
                <div key={v} className="flex items-center gap-1.5 text-xs text-amber-300 mt-1">
                  <AlertTriangle size={11} /> {v}
                </div>
              ))}
            </div>
          </div>

          {/* CERT Population Percentile Comparison */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
              Percentile vs CERT R4.2 Population
            </h3>
            {loading && <p className="text-xs text-slate-500 animate-pulse">Loading comparison…</p>}
            {error && <p className="text-xs text-red-400">{error}</p>}
            {comparison && (
              <div className="space-y-2">
                {/* Overall risk percentile */}
                <div className="rounded-lg p-3 bg-white/5 border border-white/10 mb-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-300 font-medium">Overall Risk Percentile</span>
                    <span className="text-lg font-black" style={{ color: risk.color }}>
                      {comparison.employee_risk_percentile?.toFixed(1)}th
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-slate-700 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${comparison.employee_risk_percentile || 0}%`, background: risk.color }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Population baseline: {comparison.cert_population?.total_employees?.toLocaleString()} employees ·
                    Median: {comparison.cert_population?.risk_median?.toFixed(1)} ·
                    P90: {comparison.cert_population?.risk_p90?.toFixed(1)} ·
                    P95: {comparison.cert_population?.risk_p95?.toFixed(1)}
                  </p>
                </div>

                {/* Dimension table */}
                <div className="rounded-lg overflow-hidden border border-white/10">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-white/5">
                        <th className="text-left px-3 py-2 text-slate-400 font-semibold">Dimension</th>
                        <th className="text-right px-3 py-2 text-slate-400 font-semibold">Employee</th>
                        <th className="text-right px-3 py-2 text-slate-400 font-semibold">CERT P50</th>
                        <th className="text-right px-3 py-2 text-slate-400 font-semibold">CERT P90</th>
                        <th className="text-right px-3 py-2 text-slate-400 font-semibold">Percentile</th>
                        <th className="text-right px-3 py-2 text-slate-400 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(comparison.behavioral_dimensions || []).map((dim) => (
                        <tr key={dim.dimension}
                          className="border-t border-white/5 hover:bg-white/5 transition-colors">
                          <td className="px-3 py-2 text-slate-300">{dim.dimension}</td>
                          <td className="px-3 py-2 text-right text-slate-200 font-mono">
                            {Number(dim.employee_value).toLocaleString()}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-400 font-mono">
                            {Number(dim.cert_median).toLocaleString()}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-400 font-mono">
                            {Number(dim.cert_p90).toLocaleString()}
                          </td>
                          <td className="px-3 py-2 text-right font-bold"
                            style={{ color: dim.percentile >= 90 ? "#ef4444" : dim.percentile >= 75 ? "#f59e0b" : "#22c55e" }}>
                            {dim.percentile?.toFixed(1)}th
                          </td>
                          <td className="px-3 py-2 text-right">
                            {dim.anomalous ? (
                              <span className="text-red-400 font-semibold">ANOMALOUS</span>
                            ) : (
                              <span className="text-slate-500">Normal</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-[10px] text-slate-600 italic">
                  Percentile computed against CERT R4.2 population baseline only. Employee is NOT added to the baseline.
                </p>
              </div>
            )}
          </div>

          {/* Raw features */}
          {evaluation.raw_features && (
            <div>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
                22 Behavioral Feature Values
              </h3>
              <div className="grid grid-cols-2 gap-1.5">
                {Object.entries(evaluation.raw_features).map(([k, v]) => (
                  <div key={k} className="flex justify-between rounded px-2 py-1 bg-white/5 text-xs">
                    <span className="text-slate-500 font-mono">{k}</span>
                    <span className="text-slate-300 font-mono">{Number(v).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// TAB 1 — EVALUATE NEW EMPLOYEE
// ============================================================
function TabEvaluate({ onSaved }) {
  const [identity, setIdentity] = useState({
    employee_id: "",
    employee_name: "",
    department: "",
    role: "",
  });
  const [features, setFeatures] = useState(buildDefaultFeatures());
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [savedMsg, setSavedMsg] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState(
    Object.fromEntries(FEATURE_SCHEMA.map((c) => [c.category, true]))
  );

  const handlePreset = (preset) => {
    setFeatures({ ...preset.values });
    setResult(null);
    setError(null);
    setSavedMsg(null);
  };

  const handleEvaluate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSavedMsg(null);
    try {
      const payload = {
        employee_id: identity.employee_id || "NEW-001",
        employee_name: identity.employee_name || undefined,
        department: identity.department || undefined,
        role: identity.role || undefined,
        features: Object.fromEntries(
          Object.entries(features).map(([k, v]) => [k, parseFloat(v) || 0])
        ),
      };
      const res = await employeeEvaluationService.evaluate(payload);
      setResult(res);
    } catch (e) {
      setError(e?.response?.data?.detail || "Evaluation failed. Check feature values.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    setSaving(true);
    try {
      await employeeEvaluationService.save(result);
      setSavedMsg(`✓ Evaluation for ${result.employee?.employee_id || "employee"} saved to session store.`);
      onSaved?.();
    } catch (e) {
      setError(e?.response?.data?.detail || "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  const toggleCategory = (cat) =>
    setExpandedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }));

  return (
    <div className="space-y-5">
      {/* Presets banner */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Info size={14} className="text-slate-500" />
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Demonstration / Test Vectors — NOT real CERT employee records
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.label}
              onClick={() => handlePreset(p)}
              title={p.description}
              className="px-3 py-1.5 rounded-lg text-xs font-medium border border-white/15 text-slate-300
                hover:border-cyan-500/50 hover:text-cyan-300 hover:bg-cyan-500/10 transition-all duration-150"
            >
              {p.label}
            </button>
          ))}
          <button
            onClick={() => { setFeatures(buildDefaultFeatures()); setResult(null); setError(null); setSavedMsg(null); }}
            className="px-3 py-1.5 rounded-lg text-xs font-medium border border-white/10 text-slate-500
              hover:text-slate-300 hover:border-white/25 transition-all duration-150 flex items-center gap-1"
          >
            <RotateCcw size={11} /> Reset
          </button>
        </div>
      </Card>

      {/* Identity fields */}
      <Card className="p-4">
        <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <UserPlus size={14} className="text-cyan-400" /> Employee Identity
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { key: "employee_id", label: "Employee ID", placeholder: "NEW-001" },
            { key: "employee_name", label: "Full Name", placeholder: "Jane Smith" },
            { key: "department", label: "Department", placeholder: "Engineering" },
            { key: "role", label: "Role / Title", placeholder: "Software Engineer" },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-xs text-slate-500 mb-1">{label}</label>
              <input
                id={`eval-identity-${key}`}
                type="text"
                placeholder={placeholder}
                value={identity[key]}
                onChange={(e) => setIdentity((p) => ({ ...p, [key]: e.target.value }))}
                className="w-full rounded-lg px-3 py-2 text-sm bg-white/5 border border-white/15
                  text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50
                  focus:bg-cyan-500/5 transition-all"
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Feature inputs by category */}
      {FEATURE_SCHEMA.map((cat) => {
        const Icon = cat.icon;
        const isOpen = expandedCategories[cat.category];
        return (
          <Card key={cat.category} className="overflow-hidden">
            <button
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
              onClick={() => toggleCategory(cat.category)}
            >
              <div className="flex items-center gap-2">
                <Icon size={14} style={{ color: cat.color }} />
                <span className="text-sm font-semibold text-slate-200">{cat.category}</span>
              </div>
              {isOpen ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
            </button>
            {isOpen && (
              <div className="px-4 pb-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 border-t border-white/10 pt-3">
                {cat.fields.map((f) => (
                  <div key={f.name}>
                    <label className="block text-xs text-slate-500 mb-1">{f.label}</label>
                    <input
                      id={`eval-feature-${f.name}`}
                      type="number"
                      min={f.min}
                      max={f.max}
                      step={f.step}
                      value={features[f.name] ?? f.default}
                      onChange={(e) =>
                        setFeatures((p) => ({ ...p, [f.name]: e.target.value }))
                      }
                      className="w-full rounded-lg px-3 py-2 text-sm bg-white/5 border border-white/15
                        text-slate-200 focus:outline-none focus:border-cyan-500/50 focus:bg-cyan-500/5
                        transition-all font-mono"
                    />
                  </div>
                ))}
              </div>
            )}
          </Card>
        );
      })}

      {/* Error */}
      {error && (
        <div className="rounded-lg p-3 bg-red-500/10 border border-red-500/30 flex items-start gap-2">
          <XCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      {/* Saved message */}
      {savedMsg && (
        <div className="rounded-lg p-3 bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2">
          <CheckCircle size={14} className="text-emerald-400 shrink-0" />
          <p className="text-xs text-emerald-400">{savedMsg}</p>
        </div>
      )}

      {/* Evaluate button */}
      <button
        id="btn-run-evaluation"
        onClick={handleEvaluate}
        disabled={loading}
        className="w-full py-3 rounded-xl font-bold text-sm transition-all duration-200 flex items-center justify-center gap-2"
        style={{
          background: loading
            ? "rgba(255,255,255,0.05)"
            : "linear-gradient(135deg, #0891b2, #7c3aed)",
          color: loading ? "#64748b" : "#fff",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? (
          <><RefreshCw size={15} className="animate-spin" /> Running 7-Model ML Inference…</>
        ) : (
          <><Cpu size={15} /> Run Evaluation — 7 Pre-Trained Models</>
        )}
      </button>

      {/* Result */}
      <ResultPanel result={result} onSave={handleSave} saving={saving} />
    </div>
  );
}

// ============================================================
// TAB 2 — NEWLY EVALUATED EMPLOYEES TABLE
// ============================================================
function TabEvaluated({ refresh }) {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [filterLevel, setFilterLevel] = useState("ALL");
  const [sortKey, setSortKey] = useState("risk_score");
  const [sortDir, setSortDir] = useState("desc");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const isAdmin = ["Administrator", "admin"].includes(user?.role);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await employeeEvaluationService.getAll();
      setRecords(data || []);
    } catch {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load, refresh]);

  const handleDelete = async (empId) => {
    if (!window.confirm(`Delete evaluation for ${empId}?`)) return;
    setDeletingId(empId);
    try {
      await employeeEvaluationService.deleteEvaluation(empId);
      await load();
    } catch (e) {
      alert(e?.response?.data?.detail || "Delete failed.");
    } finally {
      setDeletingId(null);
    }
  };

  // Filter + sort
  const filtered = records
    .filter((r) => {
      const empId = r.employee?.employee_id || r.employee_id || "";
      const name = r.employee?.employee_name || "";
      const dept = r.employee?.department || "";
      const q = search.toLowerCase();
      const matchesSearch = !q || empId.toLowerCase().includes(q) || name.toLowerCase().includes(q) || dept.toLowerCase().includes(q);
      const level = (r.risk_level || "").toUpperCase();
      const matchesLevel = filterLevel === "ALL" || level === filterLevel;
      return matchesSearch && matchesLevel;
    })
    .sort((a, b) => {
      let aVal = a[sortKey] ?? 0;
      let bVal = b[sortKey] ?? 0;
      if (sortKey === "employee_id") {
        aVal = a.employee?.employee_id || "";
        bVal = b.employee?.employee_id || "";
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    });

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
  };

  // Potential threats
  const threats = records.filter((r) => r.threat_status === "POTENTIAL INSIDER THREAT");

  return (
    <div className="space-y-5">
      {/* Potential threats highlight */}
      {threats.length > 0 && (
        <Card className="p-4" style={{ borderColor: "rgba(239,68,68,0.35)", background: "rgba(239,68,68,0.07)" }}>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={15} className="text-red-400" />
            <h3 className="text-sm font-bold text-red-300">
              Potential Insider Threats Among Newly Evaluated ({threats.length})
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {threats.map((r) => {
              const id = r.employee?.employee_id || "";
              const risk = getRisk(r.risk_level);
              return (
                <button key={id}
                  onClick={() => setSelectedRecord(r)}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 border border-red-500/30 bg-red-500/10
                    hover:bg-red-500/20 transition-all text-left">
                  <div>
                    <div className="text-xs font-bold text-red-300">{id}</div>
                    <div className="text-[10px] text-slate-400">{r.employee?.department} · Risk {r.risk_score?.toFixed(1)}</div>
                  </div>
                  <span style={{ color: risk.color }} className="text-xs font-bold">{r.risk_level}</span>
                </button>
              );
            })}
          </div>
        </Card>
      )}

      {/* Empty state */}
      {!loading && records.length === 0 && (
        <Card className="p-10 text-center">
          <UserPlus size={32} className="mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400 text-sm">No evaluations saved yet.</p>
          <p className="text-slate-600 text-xs mt-1">
            Use the "Evaluate New Employee" tab to run inference and save results.
          </p>
        </Card>
      )}

      {records.length > 0 && (
        <>
          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search by ID, name, or department…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg text-sm bg-white/5 border border-white/15
                  text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 transition-all"
              />
            </div>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm bg-white/5 border border-white/15 text-slate-200
                focus:outline-none focus:border-cyan-500/50 transition-all"
            >
              {["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"].map((l) => (
                <option key={l} value={l} className="bg-slate-900">{l === "ALL" ? "All Levels" : l}</option>
              ))}
            </select>
            <button onClick={load}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-white/15 text-slate-400
              hover:text-slate-200 hover:border-white/30 transition-all text-sm">
              <RefreshCw size={12} className={loading ? "animate-spin" : ""} /> Refresh
            </button>
          </div>

          {/* Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    {[
                      { label: "Employee", key: "employee_id" },
                      { label: "Dept / Role", key: null },
                      { label: "Risk Score", key: "risk_score" },
                      { label: "Risk Level", key: null },
                      { label: "Models", key: "models_triggered" },
                      { label: "Consensus", key: "consensus_percentage" },
                      { label: "Layer 2", key: null },
                      { label: "Threat Status", key: null },
                      { label: "Evaluated", key: null },
                      { label: "Actions", key: null },
                    ].map(({ label, key }) => (
                      <th key={label}
                        className={`text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap
                          ${key ? "cursor-pointer hover:text-slate-200 select-none" : ""}`}
                        onClick={key ? () => toggleSort(key) : undefined}
                      >
                        <span className="flex items-center gap-1">
                          {label}
                          {key && <ArrowUpDown size={10} className={sortKey === key ? "text-cyan-400" : "text-slate-600"} />}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((r) => {
                    const empId = r.employee?.employee_id || "";
                    const layer2 = r.layer2_verification || {};
                    const ts = r.evaluation_timestamp
                      ? new Date(r.evaluation_timestamp).toLocaleString()
                      : "—";
                    return (
                      <tr key={empId}
                        className="border-t border-white/5 hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-mono font-semibold text-slate-200 text-xs">{empId}</div>
                          <div className="text-xs text-slate-500">{r.employee?.employee_name}</div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-xs text-slate-400">{r.employee?.department}</div>
                          <div className="text-xs text-slate-500">{r.employee?.role}</div>
                        </td>
                        <td className="px-4 py-3 font-mono font-bold"
                          style={{ color: getRisk(r.risk_level).color }}>
                          {r.risk_score?.toFixed(1)}
                        </td>
                        <td className="px-4 py-3"><RiskBadge level={r.risk_level} /></td>
                        <td className="px-4 py-3 text-xs font-mono text-slate-300">
                          {r.models_triggered}/{r.models_evaluated || 7}
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-violet-400">
                          {r.consensus_percentage?.toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-xs"
                          style={{ color: layer2.supported_by_behavioral_evidence ? "#22c55e" : "#64748b" }}>
                          {layer2.supported_by_behavioral_evidence ? "✓ Supported" : "– No"}
                        </td>
                        <td className="px-4 py-3">
                          <ThreatBadge status={r.threat_status} />
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">{ts}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => setSelectedRecord(r)}
                              title="View Details"
                              className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-cyan-500/10 transition-all"
                            >
                              <Eye size={13} />
                            </button>
                            {isAdmin && (
                              <button
                                onClick={() => handleDelete(empId)}
                                disabled={deletingId === empId}
                                title="Delete (Administrator)"
                                className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all disabled:opacity-40"
                              >
                                {deletingId === empId
                                  ? <RefreshCw size={13} className="animate-spin" />
                                  : <Trash2 size={13} />}
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={10} className="px-4 py-8 text-center text-slate-500 text-xs">
                        No evaluations match your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      {selectedRecord && (
        <DetailDrawer evaluation={selectedRecord} onClose={() => setSelectedRecord(null)} />
      )}
    </div>
  );
}

// ============================================================
// TAB 3 — EXISTING vs NEW COMPARISON
// ============================================================
function TabComparison() {
  const [summary, setSummary] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingRanking, setLoadingRanking] = useState(false);
  const [selectedForComparison, setSelectedForComparison] = useState(null);
  const [rankSearch, setRankSearch] = useState("");

  const loadSummary = async () => {
    setLoadingSummary(true);
    try {
      const data = await employeeEvaluationService.getComparisonSummary();
      setSummary(data);
    } catch {
      setSummary(null);
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadRanking = async () => {
    setLoadingRanking(true);
    try {
      const data = await employeeEvaluationService.getComparisonRanking();
      setRanking(data || []);
    } catch {
      setRanking([]);
    } finally {
      setLoadingRanking(false);
    }
  };

  useEffect(() => {
    loadSummary();
    loadRanking();
  }, []);

  const cert = summary?.cert || {};
  const newPop = summary?.new || {};

  // Bar chart data: risk level distribution
  const riskDistChartData = ["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((level) => ({
    level,
    CERT: cert.risk_level_counts?.[level] || 0,
    NEW: newPop.risk_level_counts?.[level] || 0,
  }));

  // Consensus comparison
  const consensusData = [
    { name: "Avg Risk Score", CERT: cert.avg_risk_score || 0, NEW: newPop.avg_risk_score || 0 },
    { name: "Median Risk Score", CERT: cert.median_risk_score || 0, NEW: newPop.median_risk_score || 0 },
    { name: "Avg Consensus %", CERT: cert.avg_consensus_percentage || 0, NEW: newPop.avg_consensus_percentage || 0 },
  ];

  const filteredRanking = ranking.filter((r) => {
    if (!rankSearch) return true;
    const q = rankSearch.toLowerCase();
    return (
      r.employee_id?.toLowerCase().includes(q) ||
      r.employee_name?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <BarChart3 size={15} className="text-cyan-400" />
          Existing CERT R4.2 Population vs Newly Evaluated Employees
        </h2>
        <button onClick={() => { loadSummary(); loadRanking(); }}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border border-white/15
          text-slate-400 hover:text-slate-200 hover:border-white/30 transition-all">
          <RefreshCw size={11} className={(loadingSummary || loadingRanking) ? "animate-spin" : ""} /> Refresh
        </button>
      </div>

      {/* Population summary cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* CERT card */}
          <Card className="p-4" style={{ borderColor: "rgba(148,163,184,0.25)" }}>
            <div className="flex items-center gap-2 mb-4">
              <SourceBadge source="CERT_R4.2" />
              <span className="text-xs text-slate-400">{cert.total?.toLocaleString()} employees</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Stat label="Avg Risk Score" value={cert.avg_risk_score?.toFixed(1)} color="#94a3b8" />
              <Stat label="Median Risk Score" value={cert.median_risk_score?.toFixed(1)} color="#94a3b8" />
              <Stat label="Max Risk Score" value={cert.max_risk_score?.toFixed(1)} color="#ef4444" />
              <Stat label="P95 Risk Score" value={cert.p95_risk_score?.toFixed(1)} color="#f97316" />
              <Stat label="Avg Consensus" value={`${cert.avg_consensus_percentage?.toFixed(1)}%`} color="#8b5cf6" />
              <Stat label="Layer 2 Rate" value={`${cert.layer2_validation_rate?.toFixed(1)}%`} color="#06b6d4" />
            </div>
            {/* Risk level breakdown */}
            <div className="mt-4 border-t border-white/10 pt-3">
              <p className="text-xs text-slate-500 mb-2">Risk Level Distribution</p>
              <div className="grid grid-cols-4 gap-1 text-center">
                {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((l) => {
                  const cfg = getRisk(l);
                  const count = cert.risk_level_counts?.[l] || 0;
                  const pct = cert.total ? ((count / cert.total) * 100).toFixed(1) : 0;
                  return (
                    <div key={l} className="rounded-lg p-2" style={{ background: cfg.bg, borderColor: cfg.border, border: "1px solid" }}>
                      <div className="text-sm font-bold" style={{ color: cfg.color }}>{pct}%</div>
                      <div className="text-[10px] text-slate-500">{l}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>

          {/* NEW card */}
          <Card className="p-4" style={{ borderColor: "rgba(245,158,11,0.35)" }}>
            <div className="flex items-center gap-2 mb-4">
              <SourceBadge source="NEW_EVALUATION" />
              <span className="text-xs text-slate-400">{newPop.total?.toLocaleString()} employees</span>
              {newPop.potential_threat_count > 0 && (
                <span className="text-xs text-red-400 font-semibold">
                  ⚠ {newPop.potential_threat_count} potential threat{newPop.potential_threat_count > 1 ? "s" : ""}
                </span>
              )}
            </div>
            {newPop.total === 0 ? (
              <p className="text-xs text-slate-500">
                No evaluations saved yet. Evaluate employees in Tab 1 and save them.
              </p>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <Stat label="Avg Risk Score" value={newPop.avg_risk_score?.toFixed(1)} color="#f59e0b" />
                  <Stat label="Median Risk Score" value={newPop.median_risk_score?.toFixed(1)} color="#f59e0b" />
                  <Stat label="Max Risk Score" value={newPop.max_risk_score?.toFixed(1)} color="#ef4444" />
                  <Stat label="Min Risk Score" value={newPop.min_risk_score?.toFixed(1)} color="#22c55e" />
                  <Stat label="Avg Consensus" value={`${newPop.avg_consensus_percentage?.toFixed(1)}%`} color="#8b5cf6" />
                  <Stat label="Layer 2 Rate" value={`${newPop.layer2_validation_rate?.toFixed(1)}%`} color="#06b6d4" />
                </div>
                <div className="mt-4 border-t border-white/10 pt-3">
                  <p className="text-xs text-slate-500 mb-2">Risk Level Distribution</p>
                  <div className="grid grid-cols-4 gap-1 text-center">
                    {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((l) => {
                      const cfg = getRisk(l);
                      const count = newPop.risk_level_counts?.[l] || 0;
                      const pct = newPop.total ? ((count / newPop.total) * 100).toFixed(1) : 0;
                      return (
                        <div key={l} className="rounded-lg p-2" style={{ background: cfg.bg, borderColor: cfg.border, border: "1px solid" }}>
                          <div className="text-sm font-bold" style={{ color: cfg.color }}>{pct}%</div>
                          <div className="text-[10px] text-slate-500">{l}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </Card>
        </div>
      )}

      {/* Charts */}
      {summary && newPop.total > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Risk level distribution bar chart */}
          <Card className="p-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Risk Level Distribution — CERT vs New
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={riskDistChartData} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="level" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#94a3b8" }}
                />
                <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
                <Bar dataKey="CERT" fill="#475569" radius={[4, 4, 0, 0]} name="CERT R4.2" />
                <Bar dataKey="NEW" fill="#f59e0b" radius={[4, 4, 0, 0]} name="New Evaluation" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Score comparison bar chart */}
          <Card className="p-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Risk Metrics Comparison
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={consensusData} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#94a3b8" }}
                />
                <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
                <Bar dataKey="CERT" fill="#475569" radius={[4, 4, 0, 0]} name="CERT R4.2" />
                <Bar dataKey="NEW" fill="#06b6d4" radius={[4, 4, 0, 0]} name="New Evaluation" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      {/* Combined risk ranking */}
      <Card className="overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp size={13} className="text-cyan-400" />
            Combined Risk Ranking — Top 50 CERT + All New Evaluations
          </h3>
          <div className="relative">
            <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Filter ranking…"
              value={rankSearch}
              onChange={(e) => setRankSearch(e.target.value)}
              className="pl-7 pr-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/15
                text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 transition-all"
            />
          </div>
        </div>
        {loadingRanking && (
          <div className="py-10 text-center">
            <RefreshCw size={20} className="animate-spin mx-auto text-slate-600 mb-2" />
            <p className="text-xs text-slate-500">Loading ranking…</p>
          </div>
        )}
        {!loadingRanking && ranking.length === 0 && (
          <div className="py-10 text-center">
            <p className="text-xs text-slate-500">
              No CERT data loaded or no evaluations saved. Save evaluations to see the combined ranking.
            </p>
          </div>
        )}
        {!loadingRanking && ranking.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-white/5">
                  {["Rank", "Employee ID", "Name", "Source", "Risk Score", "Risk Level", "Models", "Consensus", "Layer 2"].map((h) => (
                    <th key={h} className="text-left px-3 py-2.5 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredRanking.map((r) => {
                  const isNew = r.source === "NEW_EVALUATION";
                  const risk = getRisk(r.risk_level);
                  return (
                    <tr
                      key={`${r.source}-${r.employee_id}-${r.rank}`}
                      onClick={() => isNew ? setSelectedForComparison(r) : null}
                      className={`border-t border-white/5 transition-colors
                        ${isNew ? "hover:bg-amber-500/10 cursor-pointer" : "hover:bg-white/5"}`}
                      style={isNew ? { background: "rgba(245,158,11,0.04)" } : {}}
                    >
                      <td className="px-3 py-2.5 text-xs font-bold text-slate-500">#{r.rank}</td>
                      <td className="px-3 py-2.5 font-mono text-xs font-semibold text-slate-200">
                        {r.employee_id}
                      </td>
                      <td className="px-3 py-2.5 text-xs text-slate-400">
                        {r.employee_name && r.employee_name !== r.employee_id ? r.employee_name : "—"}
                      </td>
                      <td className="px-3 py-2.5"><SourceBadge source={r.source} /></td>
                      <td className="px-3 py-2.5 font-mono font-bold" style={{ color: risk.color }}>
                        {r.risk_score?.toFixed(1)}
                      </td>
                      <td className="px-3 py-2.5"><RiskBadge level={r.risk_level} /></td>
                      <td className="px-3 py-2.5 text-xs font-mono text-slate-300">
                        {r.models_triggered > 0 ? `${r.models_triggered}/7` : "—"}
                      </td>
                      <td className="px-3 py-2.5 text-xs font-mono text-violet-400">
                        {r.consensus_percentage > 0 ? `${r.consensus_percentage?.toFixed(1)}%` : "—"}
                      </td>
                      <td className="px-3 py-2.5 text-xs text-slate-500">{r.layer2_status || "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="px-4 py-2.5 border-t border-white/10 flex items-center gap-3 text-[10px] text-slate-600">
              <span>
                <span className="inline-block w-2.5 h-2.5 rounded mr-1 align-middle" style={{ background: "rgba(148,163,184,0.3)" }} />
                CERT R4.2 (immutable reference population)
              </span>
              <span>
                <span className="inline-block w-2.5 h-2.5 rounded mr-1 align-middle" style={{ background: "rgba(245,158,11,0.4)" }} />
                NEW EVALUATION (session store) — click row for percentile comparison
              </span>
            </div>
          </div>
        )}
      </Card>

      {/* Individual comparison drawer (from ranking click) */}
      {selectedForComparison && (
        <DetailDrawer
          evaluation={selectedForComparison}
          onClose={() => setSelectedForComparison(null)}
        />
      )}
    </div>
  );
}

// ============================================================
// MAIN PAGE
// ============================================================
const TABS = [
  { id: "evaluate", label: "Evaluate New Employee", icon: UserPlus },
  { id: "evaluated", label: "Newly Evaluated Employees", icon: Users },
  { id: "comparison", label: "Existing vs New Comparison", icon: BarChart3 },
];

export default function EmployeeEvaluationPage() {
  const [activeTab, setActiveTab] = useState("evaluate");
  const [savedTick, setSavedTick] = useState(0);

  const handleSaved = () => setSavedTick((t) => t + 1);

  return (
    <div className="min-h-screen">
      {/* Page header */}
      <div className="mb-6">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-xl"
            style={{ background: "linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2))", border: "1px solid rgba(6,182,212,0.3)" }}>
            <UserPlus size={20} className="text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100">Employee Evaluation</h1>
            <p className="text-sm text-slate-400 mt-0.5">
              Evaluate new employee behavioral profiles through the existing 7-model ML pipeline
              and compare against the immutable CERT R4.2 reference population.
            </p>
          </div>
        </div>

        {/* Immutability notice */}
        <div className="mt-4 px-4 py-2.5 rounded-lg flex items-start gap-2"
          style={{ background: "rgba(6,182,212,0.06)", border: "1px solid rgba(6,182,212,0.18)" }}>
          <Shield size={13} className="text-cyan-500 mt-0.5 shrink-0" />
          <p className="text-xs text-slate-500">
            <span className="text-cyan-400 font-semibold">CERT R4.2 population remains immutable.</span>{" "}
            Newly evaluated employees are stored in the session cache with{" "}
            <code className="font-mono text-amber-400">source = "NEW_EVALUATION"</code>.
            No model retraining occurs. No datasets or model artifacts are modified.
          </p>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-5 border-b border-white/10 pb-0">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all duration-200 border-b-2 -mb-px"
              style={{
                borderColor: isActive ? "#06b6d4" : "transparent",
                color: isActive ? "#06b6d4" : "#64748b",
                background: isActive ? "rgba(6,182,212,0.08)" : "transparent",
              }}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      {activeTab === "evaluate" && <TabEvaluate onSaved={handleSaved} />}
      {activeTab === "evaluated" && <TabEvaluated refresh={savedTick} />}
      {activeTab === "comparison" && <TabComparison />}
    </div>
  );
}
