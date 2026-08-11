import { motion } from "framer-motion";

function Card({
  title,
  value,
  color,
  subtitle,
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="
        rounded-2xl
        border
        border-slate-700
        bg-slate-900/60
        p-5
      "
    >
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <h2
        className={`mt-2 text-3xl font-bold ${color}`}
      >
        {value}
      </h2>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-500">
          {subtitle}
        </p>
      )}
    </motion.div>
  );
}

export default function InvestigationOverviewCards({
  employee,
}) {
  if (!employee) {
    return null;
  }

  const riskLevel =
    employee.risk_level ??
    "Low";

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card
        title="Risk Score"
        value={Number(employee.risk_score ?? 0).toFixed(1)}
        color="text-red-400"
      />

      <Card
        title="Risk Level"
        value={riskLevel}
        color={
          riskLevel === "Critical"
            ? "text-red-400"
            : riskLevel === "High"
              ? "text-orange-400"
              : riskLevel === "Medium"
                ? "text-yellow-400"
                : "text-emerald-400"
        }
      />

      <Card
        title="Model Consensus"
        value={`${Number(
          employee.consensus_percentage ?? 0
        ).toFixed(1)}%`}
        color="text-cyan-400"
        subtitle={`${employee.suspicious_count ?? 0} / 7 models suspicious`}
      />

      <Card
        title="ML Rank"
        value={
          employee.rank
            ? `#${employee.rank}`
            : "—"
        }
        color="text-purple-400"
        subtitle={employee.prediction}
      />
    </div>
  );
}
