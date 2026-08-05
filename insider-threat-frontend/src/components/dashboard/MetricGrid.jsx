import {
  Users,
  ShieldAlert,
  Shield,
  Activity,
  BrainCircuit,
  FileText,
  Cpu,
  Gauge,
} from "lucide-react";

import MetricCard from "../ui/MetricCard";

export default function MetricGrid({ data }) {
  if (!data) return null;

  const metrics = [
    {
      title: "Employees Processed",
      value: data.employeesProcessed,
      subtitle: "Employees analyzed",
      color: "text-cyan-400",
      icon: Users,
    },
    {
      title: "Critical Employees",
      value: data.criticalEmployees,
      subtitle: "Immediate attention required",
      color: "text-red-500",
      icon: ShieldAlert,
    },
    {
      title: "High Risk",
      value: data.highRiskEmployees,
      subtitle: "High threat score",
      color: "text-orange-400",
      icon: Shield,
    },
    {
      title: "Medium Risk",
      value: data.mediumRiskEmployees,
      subtitle: "Needs monitoring",
      color: "text-yellow-400",
      icon: Activity,
    },
    {
      title: "ML Models",
      value: data.machineLearningModels,
      subtitle: `Best Model: ${data.bestModel}`,
      color: "text-purple-400",
      icon: BrainCircuit,
    },
    {
      title: "Features Generated",
      value: data.featuresGenerated,
      subtitle: "Behavioral Features",
      color: "text-green-400",
      icon: Cpu,
    },
    {
      title: "Reports Generated",
      value: data.reportsGenerated,
      subtitle: "Generated Reports",
      color: "text-pink-400",
      icon: FileText,
    },
    {
      title: "Execution Time",
      value: `${data.executionTimeSeconds}s`,
      subtitle: "Processing Time",
      color: "text-emerald-400",
      icon: Gauge,
    },
  ];

  return (
    <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <MetricCard
          key={metric.title}
          title={metric.title}
          value={metric.value}
          subtitle={metric.subtitle}
          color={metric.color}
          icon={metric.icon}
        />
      ))}
    </section>
  );
}
