import { ShieldAlert, ShieldCheck, ShieldQuestion, TrendingUp, TrendingDown, Minus } from "lucide-react";

const RISK_STYLES = {
  low: {
    ring: "ring-emerald-500/30",
    text: "text-emerald-400",
    bg: "bg-emerald-500/10",
    bar: "bg-emerald-500",
    icon: ShieldCheck,
  },
  medium: {
    ring: "ring-amber-500/30",
    text: "text-amber-400",
    bg: "bg-amber-500/10",
    bar: "bg-amber-500",
    icon: ShieldQuestion,
  },
  high: {
    ring: "ring-orange-500/30",
    text: "text-orange-400",
    bg: "bg-orange-500/10",
    bar: "bg-orange-500",
    icon: ShieldAlert,
  },
  critical: {
    ring: "ring-red-500/30",
    text: "text-red-400",
    bg: "bg-red-500/10",
    bar: "bg-red-500",
    icon: ShieldAlert,
  },
};

function TrendIcon({ trend }) {
  if (trend === "up")
    return <TrendingUp className="h-3.5 w-3.5 text-red-400" />;
  if (trend === "down")
    return <TrendingDown className="h-3.5 w-3.5 text-emerald-400" />;
  return <Minus className="h-3.5 w-3.5 text-slate-500" />;
}

/**
 * `trend` is optional ("up" | "down" | "flat"). The current Employee schema
 * (Batch 1) does not include historical scores, so this defaults to "flat"
 * unless the caller supplies a computed trend from elsewhere (e.g. the
 * Analytics or Risk modules).
 */
export default function RiskSummaryCard({ employee, trend = "flat" }) {
  const level = employee?.risk_level ?? "low";
  const score = employee?.risk_score ?? 0;
  const style = RISK_STYLES[level] ?? RISK_STYLES.low;
  const Icon = style.icon;

  return (
    <div
      className={`rounded-xl border border-slate-800 bg-slate-900/60 p-4 ring-1 ${style.ring}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`rounded-lg p-1.5 ${style.bg} ${style.text}`}>
            <Icon className="h-4 w-4" />
          </div>
          <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Risk Summary
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-slate-500">
          <TrendIcon trend={trend} />
          {trend === "up" && "Rising"}
          {trend === "down" && "Improving"}
          {trend === "flat" && "Stable"}
        </div>
      </div>

      <div className="mt-3 flex items-end justify-between">
        <div>
          <p className={`text-3xl font-bold ${style.text}`}>{score}</p>
          <p className="text-xs text-slate-500">out of 100</p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${style.bg} ${style.text}`}
        >
          {level}
        </span>
      </div>

      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full ${style.bar} transition-all duration-500`}
          style={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
        />
      </div>
    </div>
  );
}
