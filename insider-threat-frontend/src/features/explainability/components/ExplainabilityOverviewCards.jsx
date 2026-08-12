import { motion } from "framer-motion";
import {
  BrainCircuit,
  BarChart3,
  ShieldAlert,
  Users,
} from "lucide-react";
import { formatFeatureName } from "../../../utils/formatters";

function Card({
  title,
  value,
  color,
  Icon,
}) {
  const isLong = String(value).length > 15;
  const fontSizeClass = isLong ? "mt-3 text-lg font-bold truncate" : "mt-3 text-2xl font-bold";

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="
        rounded-2xl
        border
        border-slate-800
        bg-slate-900/60
        p-5
        backdrop-blur-sm
      "
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-slate-400">
          {title}
        </p>

        <Icon
          size={20}
          className={color}
        />
      </div>

      <h2 className={`${fontSizeClass} ${color}`} title={String(value)}>
        {value}
      </h2>
    </motion.div>
  );
}

export default function ExplainabilityOverviewCards({
  featureImportance = [],
  behavioralFactors = [],
}) {
  const rawTopFeature =
    featureImportance.length > 0
      ? featureImportance[0]?.Feature
      : "N/A";

  const rawTopBehavior =
    behavioralFactors.length > 0
      ? behavioralFactors[0]?.Behavior
      : "N/A";

  const topFeature = formatFeatureName(rawTopFeature);
  const topBehavior = formatFeatureName(rawTopBehavior);

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card
        title="Features Analyzed"
        value={featureImportance.length}
        color="text-cyan-400"
        Icon={BrainCircuit}
      />

      <Card
        title="Behavioral Factors"
        value={behavioralFactors.length}
        color="text-purple-400"
        Icon={BarChart3}
      />

      <Card
        title="Top Feature"
        value={topFeature}
        color="text-orange-400"
        Icon={ShieldAlert}
      />

      <Card
        title="Top Behavior"
        value={topBehavior}
        color="text-emerald-400"
        Icon={Users}
      />
    </div>
  );
}
