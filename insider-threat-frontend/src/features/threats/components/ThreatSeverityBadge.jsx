const COLORS = {
  Critical: "bg-red-600 text-white",
  High: "bg-orange-500 text-white",
  Medium: "bg-yellow-500 text-black",
  Low: "bg-green-600 text-white",
};

export default function ThreatSeverityBadge({ severity }) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${
        COLORS[severity] ??
        "bg-slate-600 text-white"
      }`}
    >
      {severity}
    </span>
  );
}
