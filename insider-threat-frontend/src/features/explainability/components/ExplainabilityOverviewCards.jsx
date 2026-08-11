import { motion } from "framer-motion";
import {
  BrainCircuit,
  BarChart3,
  ShieldAlert,
  Users,
} from "lucide-react";

function Card({
  title,
  value,
  color,
  Icon,
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      className="
        rounded-2xl
        border
        border-slate-700
        bg-slate-900/60
        p-5
      "
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {title}
        </p>

        <Icon
          size={21}
          className={color}
        />
      </div>

      <h2
        className={`mt-3 text-3xl font-bold ${color}`}
      >
        {value}
      </h2>
    </motion.div>
  );
}

export default function ExplainabilityOverviewCards({
  featureImportance,
  behavioralFactors,
}) {
  const topFeature =
    featureImportance.length > 0
      ? featureImportance[0]?.Feature
      : "N/A";

  const topBehavior =
    behavioralFactors.length > 0
      ? behavioralFactors[0]?.Behavior
      : "N/A";

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
