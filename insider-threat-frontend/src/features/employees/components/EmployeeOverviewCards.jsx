import {
  Users,
  ShieldAlert,
  AlertTriangle,
  Activity,
  ShieldCheck,
} from "lucide-react";
import MetricCard from "../../../components/shared/MetricCard";

export default function EmployeeOverviewCards({ employees = [] }) {
  const total = employees.length;

  const critical = employees.filter(
    (e) => e.risk_level?.toLowerCase() === "critical"
  ).length;

  const high = employees.filter(
    (e) => e.risk_level?.toLowerCase() === "high"
  ).length;

  const medium = employees.filter(
    (e) => e.risk_level?.toLowerCase() === "medium"
  ).length;

  const low = employees.filter(
    (e) => e.risk_level?.toLowerCase() === "low"
  ).length;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      <MetricCard
        title="Employees"
        value={total}
        icon={Users}
        color="text-cyan-400"
        bgColor="bg-cyan-500/10"
        borderColor="border-cyan-500/20"
      />

      <MetricCard
        title="Critical"
        value={critical}
        icon={ShieldAlert}
        color="text-red-400"
        bgColor="bg-red-500/10"
        borderColor="border-red-500/20"
      />

      <MetricCard
        title="High"
        value={high}
        icon={AlertTriangle}
        color="text-orange-400"
        bgColor="bg-orange-500/10"
        borderColor="border-orange-500/20"
      />

      <MetricCard
        title="Medium"
        value={medium}
        icon={Activity}
        color="text-yellow-300"
        bgColor="bg-yellow-500/10"
        borderColor="border-yellow-500/20"
      />

      <MetricCard
        title="Low"
        value={low}
        icon={ShieldCheck}
        color="text-emerald-400"
        bgColor="bg-emerald-500/10"
        borderColor="border-emerald-500/20"
      />
    </div>
  );
}
