import {
  Users,
  ShieldAlert,
  TriangleAlert,
  AlertCircle,
  ShieldCheck,
} from "lucide-react";

function Card({ title, value, icon: Icon, color }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">
            {title}
          </p>

          <h2 className="mt-2 text-3xl font-bold text-white">
            {value}
          </h2>
        </div>

        <div className={`rounded-lg p-3 ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

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
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      <Card
        title="Employees"
        value={total}
        icon={Users}
        color="bg-cyan-600"
      />

      <Card
        title="Critical"
        value={critical}
        icon={ShieldAlert}
        color="bg-red-600"
      />

      <Card
        title="High"
        value={high}
        icon={TriangleAlert}
        color="bg-orange-600"
      />

      <Card
        title="Medium"
        value={medium}
        icon={AlertCircle}
        color="bg-yellow-600"
      />

      <Card
        title="Low"
        value={low}
        icon={ShieldCheck}
        color="bg-green-600"
      />
    </div>
  );
}
