import { motion } from "framer-motion";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Activity,
  Database,
} from "lucide-react";

function OverviewCard({
  title,
  value,
  icon: Icon,
  color,
}) {
  return (
    <motion.div
      whileHover={{
        y: -6,
        scale: 1.02,
      }}
      transition={{
        duration: 0.2,
      }}
      className="
        rounded-3xl

        border
        border-white/10

        bg-white/5

        backdrop-blur-2xl

        p-6

        shadow-xl

        shadow-cyan-500/10
      "
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-sm text-slate-400 uppercase tracking-wider">
            {title}
          </p>

          <h2
            className={`mt-3 text-5xl font-bold ${color}`}
          >
            {value}
          </h2>

        </div>

        <div
          className="
            rounded-2xl

            bg-white/5

            p-4
          "
        >
          <Icon
            size={30}
            className={color}
          />
        </div>

      </div>

    </motion.div>
  );
}

export default function ThreatOverviewCards({
  threats,
}) {
  const critical =
    threats.filter(
      (t) => t.severity === "Critical"
    ).length;

  const high =
    threats.filter(
      (t) => t.severity === "High"
    ).length;

  const medium =
    threats.filter(
      (t) => t.severity === "Medium"
    ).length;

  const low =
    threats.filter(
      (t) => t.severity === "Low"
    ).length;

  const cards = [
    {
      title: "Total Threats",
      value: threats.length,
      color: "text-cyan-400",
      icon: Database,
    },
    {
      title: "Critical",
      value: critical,
      color: "text-red-500",
      icon: ShieldAlert,
    },
    {
      title: "High",
      value: high,
      color: "text-orange-400",
      icon: AlertTriangle,
    },
    {
      title: "Medium",
      value: medium,
      color: "text-yellow-400",
      icon: Activity,
    },
    {
      title: "Low",
      value: low,
      color: "text-green-400",
      icon: ShieldCheck,
    },
  ];

  return (
    <section
      className="
        grid

        grid-cols-1

        sm:grid-cols-2

        xl:grid-cols-5

        gap-6
      "
    >
      {cards.map((card) => (
        <OverviewCard
          key={card.title}
          {...card}
        />
      ))}
    </section>
  );
}
