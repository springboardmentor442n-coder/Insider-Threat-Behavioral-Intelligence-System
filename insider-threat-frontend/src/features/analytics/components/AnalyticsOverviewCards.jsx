import { motion } from "framer-motion";
import {
  Users,
  ShieldAlert,
  BrainCircuit,
  Database,
  Activity,
  FileBarChart2,
  Timer,
  Layers3,
} from "lucide-react";

const cards = [
  {
    key: "employees",
    title: "Employees",
    icon: Users,
    color: "text-cyan-400",
  },
  {
    key: "critical",
    title: "Critical Risk",
    icon: ShieldAlert,
    color: "text-red-500",
  },
  {
    key: "high",
    title: "High Risk",
    icon: ShieldAlert,
    color: "text-orange-400",
  },
  {
    key: "models",
    title: "ML Models",
    icon: BrainCircuit,
    color: "text-purple-400",
  },
  {
    key: "features",
    title: "Features",
    icon: Database,
    color: "text-emerald-400",
  },
  {
    key: "reports",
    title: "Reports",
    icon: FileBarChart2,
    color: "text-pink-400",
  },
  {
    key: "execution_time",
    title: "Execution (s)",
    icon: Timer,
    color: "text-yellow-400",
  },
  {
    key: "low",
    title: "Low Risk",
    icon: Layers3,
    color: "text-green-400",
  },
];

export default function AnalyticsOverviewCards({
  summary,
}) {
  if (!summary) return null;

  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => {
        const Icon = card.icon;

        return (
          <motion.div
            key={card.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{
              y: -4,
              scale: 1.02,
            }}
            className="rounded-2xl border border-slate-700/80 bg-slate-900/70 backdrop-blur-lg p-4"
          >
            <div className="flex items-center justify-between">
              <Icon className={`h-6 w-6 ${card.color}`} />

              <Activity className="text-slate-500 h-5 w-5" />
            </div>

            <div className="mt-3">
              <h3 className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                {card.title}
              </h3>

              <p className="text-xl font-bold text-white mt-1">
                {summary[card.key]}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
