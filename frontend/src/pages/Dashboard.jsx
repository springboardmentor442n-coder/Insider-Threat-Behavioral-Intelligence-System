import { useEffect, useState } from "react";
import axios from "axios";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

import {
  FaUsers,
  FaChartLine,
  FaExclamationTriangle,
  FaCheckCircle,
  FaBullseye,
} from "react-icons/fa";

import { motion } from "framer-motion";

import {
  Pie
} from "react-chartjs-2";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

export default function Dashboard() {

  const [stats, setStats] = useState({
    total_employees: 0,
    total_predictions: 0,
    high_risk: 0,
    low_risk: 0,
    average_confidence: 0,
  });

  const [topRisk, setTopRisk] = useState([]);

  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {

    try {

      const statsRes = await axios.get(
        "http://127.0.0.1:8000/dashboard/stats"
      );

      const riskRes = await axios.get(
        "http://127.0.0.1:8000/dashboard/top-risk"
      );

      const alertsRes = await axios.get(
        "http://127.0.0.1:8000/dashboard/recent-alerts"
      );

      setStats(statsRes.data);
      setTopRisk(riskRes.data);
      setAlerts(alertsRes.data);

    } catch (err) {

      console.error(err);

    }

  }

  const pieData = {

    labels: [
      "High Risk",
      "Safe Users",
    ],

    datasets: [

      {

        data: [
          stats.high_risk,
          stats.low_risk,
        ],

        backgroundColor: [

          "#ef4444",

          "#22c55e",

        ],

        borderWidth: 0,

      },

    ],

  };
  const exportCSV = () => {
  if (topRisk.length === 0) {
    alert("No data available to export.");
    return;
  }

  const headers = [
    "Employee",
    "Risk Score",
    "Confidence",
    "Status",
  ];

  const rows = topRisk.map((emp) => [
    emp.employee_name || emp.employee_id || "Unknown",
    emp.risk_score ?? "-",
    emp.confidence
      ? `${Number(emp.confidence).toFixed(1)}%`
      : "-",
    "High Risk",
  ]);

  const csvContent =
    [headers, ...rows]
      .map((e) => e.join(","))
      .join("\n");

  const blob = new Blob([csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = "insider_threat_report.csv";

  link.click();

  URL.revokeObjectURL(url);
};
const exportPDF = () => {
  if (topRisk.length === 0) {
    alert("No data available to export.");
    return;
  }

  const doc = new jsPDF();

  doc.setFontSize(18);

  doc.text(
    "AI Insider Threat Detection Report",
    14,
    20
  );

  doc.setFontSize(11);

  doc.text(
    `Generated: ${new Date().toLocaleString()}`,
    14,
    30
  );

  autoTable(doc, {
    startY: 40,

    head: [[
      "Employee",
      "Risk Score",
      "Confidence",
      "Status",
    ]],

    body: topRisk.map((emp) => [
      emp.employee_name || emp.employee_id || "Unknown",
      emp.risk_score ?? "-",
      emp.confidence
        ? `${Number(emp.confidence).toFixed(1)}%`
        : "-",
      "High Risk",
    ]),
  });

  doc.save("insider_threat_report.pdf");
};

 return (
  <Layout title="Executive Dashboard">

    {/* ================= HEADER ================= */}

    <motion.div
      initial={{ opacity: 0, y: 25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between"
    >

      <div>

        <h2 className="text-4xl font-bold text-white">
          AI Insider Threat Behavioural Intelligence System
        </h2>

        <p className="mt-2 text-slate-400">
          Enterprise dashboard for behavioural analysis and insider threat
          detection using Machine Learning.
        </p>

      </div>

      <div className="flex gap-4">

        <button
          onClick={exportCSV}
          className="rounded-xl bg-cyan-600 px-5 py-3 font-semibold transition hover:bg-cyan-500"
        >
          📄 Export CSV
        </button>

        <button
          onClick={exportPDF}
          className="rounded-xl bg-red-600 px-5 py-3 font-semibold transition hover:bg-red-500"
        >
          📑 Export PDF
        </button>

      </div>

    </motion.div>


    {/* ================= STAT CARDS ================= */}

    <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-5">

      <StatCard
    title="Employees"
    value={stats.total_employees}
    color="#38bdf8"
    subtitle="Registered"
    icon={<FaUsers color="#38bdf8" size={32} />}
/>

<StatCard
    title="Predictions"
    value={stats.total_predictions}
    color="#f59e0b"
    subtitle="Generated"
    icon={<FaChartLine color="#f59e0b" size={32} />}
/>

<StatCard
    title="High Risk"
    value={stats.high_risk}
    color="#ef4444"
    subtitle="Requires Action"
    icon={<FaExclamationTriangle color="#ef4444" size={32} />}
/>

<StatCard
    title="Safe Users"
    value={stats.low_risk}
    color="#22c55e"
    subtitle="No Threats"
    icon={<FaCheckCircle color="#22c55e" size={32} />}
/>

<StatCard
    title="Accuracy"
    value={`${Number(stats.average_confidence || 0).toFixed(1)}%`}
    color="#a855f7"
    subtitle="Random Forest"
    icon={<FaBullseye color="#a855f7" size={32} />}
/>

    </div>


    {/* ================= ROW 1 ================= */}


{/* ================= TOP RISK EMPLOYEES ================= */}
    <motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ delay: 0.9 }}
  className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl"
>

  <div className="mb-6 flex items-center justify-between">

    <h2 className="text-2xl font-bold text-white">
      🚨 Top Risk Employees
    </h2>

    <span className="rounded-full bg-red-500/20 px-3 py-1 text-sm font-semibold text-red-400">
      {topRisk.length} Employees
    </span>

  </div>

  <div className="overflow-x-auto">

    <table className="w-full">

      <thead>

        <tr className="border-b border-slate-700 text-left text-sm font-semibold uppercase tracking-wider text-slate-400">

          <th className="pb-4">Employee</th>
          <th className="pb-4">Risk Score</th>
          <th className="pb-4">Confidence</th>
          <th className="pb-4">Status</th>

        </tr>

      </thead>

      <tbody>

        {topRisk.length === 0 ? (

          <tr>

            <td
              colSpan="4"
              className="py-8 text-center text-slate-400"
            >
              No high-risk employees found.
            </td>

          </tr>

        ) : (

          topRisk.map((emp, index) => (

            <tr
              key={index}
              className="border-b border-slate-800 transition hover:bg-slate-800/50"
            >

              <td className="py-4 font-medium text-white">
                {emp.employee_name || emp.employee_id || "Unknown"}
              </td>

              <td className="py-4">

                <span className="rounded-full bg-red-500/20 px-4 py-1 text-sm font-semibold text-red-400">
                  {emp.risk_score ?? "-"}
                </span>

              </td>

              <td className="py-4">

                <span className="font-semibold text-cyan-400">
                  {emp.confidence
                    ? `${Number(emp.confidence).toFixed(1)}%`
                    : "-"}
                </span>

              </td>

              <td className="py-4">

                <span className="rounded-full bg-red-600 px-4 py-1 text-sm font-semibold text-white">
                  High Risk
                </span>

              </td>

            </tr>

          ))

        )}

      </tbody>

    </table>

  </div>

</motion.div>



{/* ================= RECENT ALERTS ================= */}

<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ delay: 1 }}
  className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl"
>

  <div className="mb-6 flex items-center justify-between">

    <h2 className="text-2xl font-bold text-white">
      🔔 Recent Threat Alerts
    </h2>

    <span className="rounded-full bg-yellow-500/20 px-3 py-1 text-sm font-semibold text-yellow-400">
      {alerts.length} Alerts
    </span>

  </div>

  <div className="overflow-x-auto">

    <table className="w-full">

      <thead>

        <tr className="border-b border-slate-700 text-left text-sm font-semibold uppercase tracking-wider text-slate-400">

          <th className="pb-4">Employee</th>
          <th className="pb-4">Alert Type</th>
          <th className="pb-4">Time</th>

        </tr>

      </thead>

      <tbody>

        {alerts.length === 0 ? (

          <tr>

            <td
              colSpan="3"
              className="py-8 text-center text-slate-400"
            >
              No alerts available.
            </td>

          </tr>

        ) : (

          alerts.map((alert, index) => (

            <tr
              key={index}
              className="border-b border-slate-800 transition hover:bg-slate-800/50"
            >

              <td className="py-4 font-medium text-white">
                {alert.employee_name || alert.employee_id || "Unknown"}
              </td>

              <td className="py-4">

                <span className="rounded-full bg-yellow-500/20 px-4 py-1 text-sm font-semibold text-yellow-400">
                  {alert.alert_type ||
                    alert.risk_reasons ||
                    "Threat Detected"}
                </span>

              </td>

              <td className="py-4 font-medium text-slate-300">
                {alert.timestamp || "-"}
              </td>

            </tr>

          ))

        )}

      </tbody>

    </table>

  </div>

</motion.div>



{/* ================= FOOTER ================= */}

<div className="mt-6 mb-6 text-center text-sm text-slate-500">

  AI Insider Threat Behavioural Intelligence System • Version 1.0 •
  Random Forest • CERT v4.2 Dataset

</div>

</Layout>
);
}