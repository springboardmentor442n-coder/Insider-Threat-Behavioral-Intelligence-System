const STYLES = {
  Critical: "border border-red-500/30 bg-red-500/15 text-red-400 shadow-sm shadow-red-500/10",
  High: "border border-orange-500/30 bg-orange-500/15 text-orange-400 shadow-sm shadow-orange-500/10",
  Medium: "border border-yellow-500/30 bg-yellow-500/15 text-yellow-300 shadow-sm shadow-yellow-500/10",
  Low: "border border-emerald-500/30 bg-emerald-500/15 text-emerald-400 shadow-sm shadow-emerald-500/10",
};

export default function ThreatSeverityBadge({ severity }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold backdrop-blur-md ${
        STYLES[severity] ?? "border border-slate-700 bg-slate-800/60 text-slate-300"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          severity === "Critical"
            ? "bg-red-400 animate-pulse"
            : severity === "High"
              ? "bg-orange-400"
              : severity === "Medium"
                ? "bg-yellow-400"
                : "bg-emerald-400"
        }`}
      />
      {severity}
    </span>
  );
}
