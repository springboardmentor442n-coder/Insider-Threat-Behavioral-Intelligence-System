import GlassCard from "../ui/GlassCard";
import { useRiskDistribution } from "../../hooks/queries/useRiskDistribution";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

const SEVERITY_COLORS = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

export default function ThreatTrendChart() {
  const { data, isLoading } = useRiskDistribution();

  if (isLoading) {
    return (
      <GlassCard className="h-[420px] flex items-center justify-center">
        Loading Risk Analytics...
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6 h-[420px]">
      <h2 className="text-xl font-semibold mb-6">
        Risk Distribution
      </h2>

      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

          <XAxis dataKey="Risk Level" stroke="#94a3b8" />

          <YAxis stroke="#94a3b8" />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              borderColor: "#334155",
              borderRadius: "0.75rem",
              color: "#f8fafc",
            }}
          />

          <Bar
            dataKey="Employees"
            radius={[6, 6, 0, 0]}
          >
            {Array.isArray(data) &&
              data.map((entry, index) => {
                const level = entry["Risk Level"] || entry["level"] || entry["name"];
                const color = SEVERITY_COLORS[level] || "#06b6d4";
                return <Cell key={`cell-${index}`} fill={color} />;
              })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </GlassCard>
  );
}
