import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Activity,
  Database,
} from "lucide-react";
import MetricCard from "../../../components/shared/MetricCard";

export default function ThreatOverviewCards({
  threats,
}) {
  const critical = threats.filter((t) => t.severity === "Critical").length;
  const high = threats.filter((t) => t.severity === "High").length;
  const medium = threats.filter((t) => t.severity === "Medium").length;
  const low = threats.filter((t) => t.severity === "Low").length;

  const cards = [
    {
      title: "Total Threats",
      value: threats.length,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/20",
      icon: Database,
    },
    {
      title: "Critical",
      value: critical,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20",
      icon: ShieldAlert,
    },
    {
      title: "High",
      value: high,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/20",
      icon: AlertTriangle,
    },
    {
      title: "Medium",
      value: medium,
      color: "text-yellow-300",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/20",
      icon: Activity,
    },
    {
      title: "Low",
      value: low,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/20",
      icon: ShieldCheck,
    },
  ];

  return (
    <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {cards.map((card) => (
        <MetricCard key={card.title} {...card} />
      ))}
    </section>
  );
}
