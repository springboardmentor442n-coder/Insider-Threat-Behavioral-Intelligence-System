import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function MonthlyTrendChart({ data = [] }) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-6">
      <h2 className="mb-5 text-xl font-semibold text-white">
        Model Training Time
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="model" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="trainingTime"
              stroke="#06b6d4"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
