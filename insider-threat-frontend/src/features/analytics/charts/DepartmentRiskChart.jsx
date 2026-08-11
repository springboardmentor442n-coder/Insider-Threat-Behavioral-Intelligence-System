import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function DepartmentRiskChart({ data = [] }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-6">
      <h2 className="mb-5 text-xl font-semibold text-white">
        Feature Statistics
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.slice(0, 8)}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis
              dataKey="feature"
              angle={-20}
              textAnchor="end"
              height={70}
            />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="mean"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
