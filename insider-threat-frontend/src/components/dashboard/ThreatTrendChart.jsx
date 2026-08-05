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
} from "recharts";

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
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="Risk Level" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="Employees"
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </GlassCard>
  );
}
