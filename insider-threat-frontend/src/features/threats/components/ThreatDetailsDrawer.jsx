import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  User,
  Building2,
  CalendarDays,
  ShieldAlert,
  Cpu,
  Activity,
  Sparkles,
  BrainCircuit,
  ArrowRight,
  CheckCircle2,
  Trash2,
} from "lucide-react";

import ThreatSeverityBadge from "./ThreatSeverityBadge";
import investigationService from "../../investigation/api/investigationService";
import { formatDate, formatScore, formatPercent } from "../../../utils/formatters";

function StatusBadge({ status }) {
  const styles = {
    Open: "bg-red-500/15 text-red-300 border border-red-500/30 shadow-sm shadow-red-500/10",
    Resolved: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm shadow-emerald-500/10",
    Investigating: "bg-yellow-500/15 text-yellow-300 border border-yellow-500/30 shadow-sm shadow-yellow-500/10",
  };

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold backdrop-blur-md ${styles[status] || "bg-slate-800 text-slate-300 border border-slate-700"}`}>
      {status}
    </span>
  );
}

function RiskScoreGauge({ score }) {
  const percentage = Math.min(score, 100);
  let colorClass = "#38bdf8";
  if (score >= 80) colorClass = "#ef4444";
  else if (score >= 60) colorClass = "#f97316";
  else if (score >= 30) colorClass = "#eab308";

  return (
    <div className="relative flex items-center justify-center">
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r="62" stroke="#1e293b" strokeWidth="8" fill="transparent" />
        <motion.circle
          cx="75"
          cy="75"
          r="62"
          stroke={colorClass}
          strokeWidth="8"
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={390}
          initial={{ strokeDashoffset: 390 }}
          animate={{ strokeDashoffset: 390 - (390 * percentage) / 100 }}
          transition={{ duration: 0.8 }}
          transform="rotate(-90 75 75)"
        />
      </svg>
      <div className="absolute text-center">
        <h1 className="text-3xl font-extrabold font-mono text-white">
          {formatScore(score)}
        </h1>
        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Risk Score
        </p>
      </div>
    </div>
  );
}

function DetailCard({ icon: Icon, title, value }) {
  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <Icon size={16} className="text-cyan-400" />
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
      </div>
      <h3 className="mt-2 text-sm font-bold text-slate-100">{value || "N/A"}</h3>
    </div>
  );
}

export default function ThreatDetailsDrawer({
  open,
  threat,
  onClose,
  onResolve,
  onDelete,
}) {
  const navigate = useNavigate();

  const handleCreateInvestigation = async () => {
    if (!threat) return;
    const empId = threat.user || threat.employee_name || threat.employee_id || threat.id;
    try {
      await investigationService.createCase(empId);
      onClose();
      navigate("/investigation");
    } catch (err) {
      console.error("Error creating investigation:", err);
    }
  };

  if (!open || !threat) return null;

  const effectiveRiskLevel = threat.risk_level || threat.severity || "Medium";
  const modelsTriggered = threat.suspicious_count || (threat.risk_score >= 80 ? 7 : threat.risk_score >= 60 ? 5 : 3);
  const consensusPct = threat.consensus_percentage || (modelsTriggered / 7) * 100;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/80 backdrop-blur-sm"
          onClick={onClose}
        />

        <motion.div
          initial={{ x: 700 }}
          animate={{ x: 0 }}
          exit={{ x: 700 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="relative w-full max-w-xl border-l border-slate-800/90 bg-slate-950/95 backdrop-blur-2xl shadow-2xl shadow-cyan-950/30 overflow-y-auto flex flex-col justify-between"
        >
          {/* Header */}
          <div className="sticky top-0 z-20 border-b border-slate-800/90 bg-slate-950/90 p-5 backdrop-blur-xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <ShieldAlert size={20} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">
                  {threat.employee_name || threat.user || `Employee ${threat.employee_id}`}
                </h2>
                <p className="text-xs font-mono text-slate-400">
                  ID #{threat.employee_id || threat.user} • {threat.department || "Engineering"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <ThreatSeverityBadge severity={threat.severity} />
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Drawer Body */}
          <div className="space-y-6 p-6 flex-1">
            {/* Risk Gauge & Consensus Summary Card */}
            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-6 backdrop-blur-xl">
              <div className="flex flex-col md:flex-row items-center justify-around gap-6">
                <RiskScoreGauge score={threat.risk_score} />

                <div className="space-y-3 text-center md:text-left">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Calculated Risk Tier</span>
                    <p className={`text-xl font-extrabold ${
                      effectiveRiskLevel === "Critical" ? "text-red-400" :
                      effectiveRiskLevel === "High" ? "text-orange-400" :
                      effectiveRiskLevel === "Medium" ? "text-yellow-300" : "text-emerald-400"
                    }`}>
                      {effectiveRiskLevel} Severity
                    </p>
                  </div>

                  <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/10 p-3">
                    <div className="flex items-center gap-2 text-cyan-300 text-xs font-bold">
                      <BrainCircuit size={16} />
                      Ensemble Model Consensus
                    </div>
                    <p className="mt-1 text-sm font-extrabold text-white">
                      {modelsTriggered} of 7 ML Models Triggered ({formatPercent(consensusPct)})
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 gap-3">
              <DetailCard icon={User} title="Employee" value={threat.employee_name || threat.user || threat.employee_id} />
              <DetailCard icon={Building2} title="Department" value={threat.department || "Engineering"} />
              <DetailCard icon={ShieldAlert} title="Threat Pattern" value={threat.threat_type || "Behavioral Anomaly"} />
              <DetailCard icon={CalendarDays} title="Detected At" value={formatDate(threat.created_at)} />
            </div>

            {/* Threat Description */}
            <div>
              <h3 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
                <Activity size={16} className="text-cyan-400" />
                Behavioral Threat Summary
              </h3>
              <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 text-xs leading-relaxed text-slate-300 backdrop-blur-xl">
                {threat.description || "Multi-model ensemble anomaly detection alert."}
              </div>
            </div>

            {/* Behavioral Evidence */}
            <div>
              <h3 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
                <Cpu size={16} className="text-cyan-400" />
                Behavioral Evidence & Indicators
              </h3>
              <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 text-xs leading-relaxed text-slate-300 backdrop-blur-xl">
                {Array.isArray(threat.evidence) ? (
                  <ul className="space-y-1.5 list-disc list-inside text-slate-300">
                    {threat.evidence.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p>{threat.evidence || "Behavioral evidence associated with anomalous activity patterns."}</p>
                )}
              </div>
            </div>

            {/* AI Analysis */}
            <div>
              <h3 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
                <BrainCircuit size={16} className="text-cyan-400" />
                AI Diagnostic Analysis
              </h3>
              <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4 text-xs leading-relaxed text-slate-300 backdrop-blur-xl">
                <div className="flex items-start gap-3">
                  <Sparkles size={18} className="mt-0.5 text-cyan-400 shrink-0" />
                  <p>
                    Ensemble AI evaluated this employee's activity as{" "}
                    <strong className="text-cyan-300">{effectiveRiskLevel} Risk</strong>{" "}
                    based on statistical outlier scoring across login hours, removable media access, web browsing patterns, and email transmission volumes.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="sticky bottom-0 border-t border-slate-800/90 bg-slate-950/90 p-5 backdrop-blur-xl space-y-3">
            <button
              type="button"
              onClick={handleCreateInvestigation}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 text-xs font-extrabold text-white shadow-lg shadow-cyan-500/25 transition hover:from-cyan-400 hover:to-blue-500"
            >
              <ShieldAlert size={16} />
              Create / Open Investigation
              <ArrowRight size={16} />
            </button>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={onResolve}
                className="flex items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 py-2.5 text-xs font-bold text-emerald-300 transition hover:bg-emerald-500/20"
              >
                <CheckCircle2 size={15} />
                Resolve Threat
              </button>

              <button
                type="button"
                onClick={onDelete}
                className="flex items-center justify-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 py-2.5 text-xs font-bold text-red-300 transition hover:bg-red-500/20"
              >
                <Trash2 size={15} />
                Delete Threat
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
