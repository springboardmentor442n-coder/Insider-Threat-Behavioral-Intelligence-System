import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Cell,
} from "recharts";

const COLORS = [
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#dc2626",
];

export default function RiskDistributionChart({ data = [] }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-6">
      <h2 className="mb-5 text-xl font-semibold text-white">
        Risk Distribution
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="level"
              outerRadius={110}
            >
              {data.map((_, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
