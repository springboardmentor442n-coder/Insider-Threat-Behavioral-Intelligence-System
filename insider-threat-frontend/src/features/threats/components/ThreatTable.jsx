import ThreatRow from "./ThreatRow";
import { ShieldAlert } from "lucide-react";

export default function ThreatTable({
  threats,
  onRowClick,
}) {
  if (!threats.length) {
    return (
      <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-12 text-center backdrop-blur-xl shadow-lg">
        <div className="flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
            <ShieldAlert size={24} />
          </div>
        </div>
        <h2 className="mt-4 text-xl font-bold text-white">
          No Threat Records Found
        </h2>
        <p className="mt-2 text-xs text-slate-400">
          No active behavioral anomalies match your selected filters or search query.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-xl shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1100px] border-collapse text-left text-xs">
          <thead className="sticky top-0 z-10 border-b border-slate-800/80 bg-slate-950/90 text-[11px] font-bold uppercase tracking-wider text-slate-400 backdrop-blur-md">
            <tr>
              <th className="px-5 py-3.5">Employee Identity</th>
              <th className="px-5 py-3.5">Department</th>
              <th className="px-5 py-3.5">Threat Pattern</th>
              <th className="px-5 py-3.5 text-center">Risk Score</th>
              <th className="px-5 py-3.5 text-center">Model Consensus</th>
              <th className="px-5 py-3.5 text-center">Severity</th>
              <th className="px-5 py-3.5 text-center">Status</th>
              <th className="px-5 py-3.5 text-center">Detected Date</th>
              <th className="px-5 py-3.5 text-right">Action</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/60">
            {threats.map((threat) => (
              <ThreatRow
                key={threat.id || threat.user || threat.employee_id}
                threat={threat}
                onClick={onRowClick}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
