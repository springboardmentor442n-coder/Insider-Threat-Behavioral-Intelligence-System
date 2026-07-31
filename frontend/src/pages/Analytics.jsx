import { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import Layout from "../components/Layout";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

export default function Analytics() {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const res = await axios.get("http://127.0.0.1:8000/predictions");
      setPredictions(res.data);
    } catch (err) {
      console.error(err);
    }
  }

  const total = predictions.length;
  const highRisk = predictions.filter(p => p.risk_level === "HIGH").length;
  const lowRisk = predictions.filter(p => p.risk_level === "LOW").length;

  const departments = {};

  predictions.forEach((p) => {
    departments[p.department] = (departments[p.department] || 0) + 1;
  });

  const pieData = {
    labels: ["High Risk", "Low Risk"],
    datasets: [
      {
        data: [highRisk, lowRisk],
        backgroundColor: ["#ef4444", "#22c55e"],
      },
    ],
  };

  const barData = {
    labels: Object.keys(departments),
    datasets: [
      {
        label: "Predictions",
        data: Object.values(departments),
        backgroundColor: "#06b6d4",
      },
    ],
  };

  return (
    <Layout title="Analytics Dashboard">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <h1 className="text-4xl font-bold text-white">
          Analytics Dashboard
        </h1>

        <p className="mt-2 text-slate-400">
          Overview of insider threat prediction statistics.
        </p>
      </motion.div>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6">
          <p className="text-slate-400">Total Predictions</p>
          <h2 className="mt-3 text-4xl font-bold text-cyan-400">
            {total}
          </h2>
        </div>

        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6">
          <p className="text-slate-400">High Risk</p>
          <h2 className="mt-3 text-4xl font-bold text-red-400">
            {highRisk}
          </h2>
        </div>

        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6">
          <p className="text-slate-400">Low Risk</p>
          <h2 className="mt-3 text-4xl font-bold text-green-400">
            {lowRisk}
          </h2>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6">
          <h2 className="mb-4 text-xl font-bold text-white">
            Risk Distribution
          </h2>

          <Pie data={pieData} />
        </div>

        <div className="rounded-2xl bg-slate-900 border border-slate-700 p-6">
          <h2 className="mb-4 text-xl font-bold text-white">
            Department Analysis
          </h2>

          <Bar
            data={barData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  display: false,
                },
              },
            }}
          />
        </div>
      </div>

      <div className="mt-8 rounded-2xl bg-slate-900 border border-slate-700 p-6">
        <h2 className="mb-4 text-xl font-bold text-white">
          AI Insights
        </h2>

        <ul className="space-y-3 text-slate-300">
          <li>• Total behavioural events analysed: {total}</li>
          <li>• High-risk activities detected: {highRisk}</li>
          <li>• Low-risk activities detected: {lowRisk}</li>
          <li>
            • The dashboard provides an overview of prediction trends across
            departments.
          </li>
        </ul>
      </div>
    </Layout>
  );
}