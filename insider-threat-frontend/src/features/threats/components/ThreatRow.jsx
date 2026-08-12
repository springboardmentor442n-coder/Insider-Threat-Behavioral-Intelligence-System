import { motion } from "framer-motion";
import { ChevronRight, ShieldAlert } from "lucide-react";
import ThreatSeverityBadge from "./ThreatSeverityBadge";
import { formatDate, formatScore, formatPercent } from "../../../utils/formatters";

function EmployeeAvatar({ name }) {
  const initials = name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();

  return (
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-indigo-500/20 border border-cyan-500/30 text-xs font-extrabold text-cyan-300 shadow-md">
      {initials || "EMP"}
    </div>
  );
}

function StatusBadge({ status }) {
  let style = "bg-slate-800 text-slate-300 border border-slate-700";

  if (status === "Open")
    style = "bg-red-500/15 text-red-300 border border-red-500/30 shadow-sm shadow-red-500/10";
  if (status === "Resolved")
    style = "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm shadow-emerald-500/10";
  if (status === "Investigating")
    style = "bg-yellow-500/15 text-yellow-300 border border-yellow-500/30 shadow-sm shadow-yellow-500/10";

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-0.5 text-xs font-semibold backdrop-blur-md ${style}`}>
      {status}
    </span>
  );
}

function RiskScorePill({ score }) {
  let color = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
  if (score >= 80) color = "text-red-400 bg-red-500/10 border-red-500/20";
  else if (score >= 60) color = "text-orange-400 bg-orange-500/10 border-orange-500/20";
  else if (score >= 30) color = "text-yellow-300 bg-yellow-500/10 border-yellow-500/20";

  return (
    <span className={`inline-flex items-center rounded-lg border px-2.5 py-1 font-mono text-xs font-extrabold ${color}`}>
      {formatScore(score)}
    </span>
  );
}

export default function ThreatRow({ threat, onClick }) {
  const modelsTriggered = threat.suspicious_count || (threat.risk_score >= 80 ? 7 : threat.risk_score >= 60 ? 5 : 3);
  const consensusPct = threat.consensus_percentage || (modelsTriggered / 7) * 100;

  return (
    <tr
      onClick={() => onClick(threat)}
      className="group cursor-pointer border-b border-slate-800/60 transition-colors hover:bg-cyan-500/5"
    >
      <td className="px-5 py-4">
        <div className="flex items-center gap-3">
          <EmployeeAvatar name={threat.employee_name || threat.user || threat.employee_id} />
          <div>
            <h3 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
              {threat.employee_name || threat.user || `Employee ${threat.employee_id}`}
            </h3>
            <p className="text-[11px] font-mono text-slate-400">
              ID #{threat.employee_id || threat.user}
            </p>
          </div>
        </div>
      </td>

      <td className="px-5 text-xs text-slate-300 font-medium">
        {threat.department || "Engineering"}
      </td>

      <td className="px-5">
        <div>
          <p className="text-xs font-semibold text-slate-200">
            {threat.threat_type || "Behavioral Anomaly"}
          </p>
          <p className="text-[11px] text-slate-400 line-clamp-1">
            {threat.description || "Multi-model ensemble anomaly detection alert."}
          </p>
        </div>
      </td>

      <td className="px-5 text-center">
        <RiskScorePill score={threat.risk_score} />
      </td>

      <td className="px-5 text-center">
        <div className="flex flex-col items-center gap-0.5">
          <span className="font-mono text-xs font-bold text-cyan-300">
            {modelsTriggered} / 7 Models
          </span>
          <span className="text-[10px] text-slate-400">
            {formatPercent(consensusPct)}
          </span>
        </div>
      </td>

      <td className="px-5 text-center">
        <ThreatSeverityBadge severity={threat.severity} />
      </td>

      <td className="px-5 text-center">
        <StatusBadge status={threat.status} />
      </td>

      <td className="px-5 text-center whitespace-nowrap text-xs font-mono text-slate-400">
        {formatDate(threat.created_at)}
      </td>

      <td className="px-5 text-right">
        <span className="inline-flex items-center gap-1 rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300 opacity-80 group-hover:opacity-100 group-hover:border-cyan-500/40 group-hover:bg-cyan-500/20 transition-all">
          Inspect
          <ChevronRight className="h-3.5 w-3.5" />
        </span>
      </td>
    </tr>
  );
}
