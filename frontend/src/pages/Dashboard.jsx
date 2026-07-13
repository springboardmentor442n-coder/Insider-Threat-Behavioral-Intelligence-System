import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import api from "../services/api";
import "../styles/Dashboard.css";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

const COLORS = ["#4ade80", "#f97316"];

const barData = [
  { department: "HR", employees: 40 },
  { department: "Finance", employees: 60 },
  { department: "IT", employees: 90 },
  { department: "Sales", employees: 60 },
];

function Dashboard() {
  const [stats, setStats] = useState({
    total_employees: 0,
    total_predictions: 0,
    high_risk: 0,
    low_risk: 0,
  });

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await api.get("/dashboard");
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    }
  };

  const pieData = [
    { name: "Safe", value: stats.low_risk },
    { name: "Risk", value: stats.high_risk },
  ];

  return (
    <div className="dashboard-layout">
      <Sidebar />

      <div className="dashboard-content">
        <h1>Dashboard</h1>
        <p>Insider Threat Behavioral Intelligence System</p>

        <div className="stats-grid">
          <StatCard
            title="Employees"
            value={stats.total_employees}
            color="#67e8f9"
          />

          <StatCard
            title="Threat Alerts"
            value={stats.total_predictions}
            color="#f59e0b"
          />

          <StatCard
            title="Risk Users"
            value={stats.high_risk}
            color="#ef4444"
          />

          <StatCard
            title="Safe Users"
            value={stats.low_risk}
            color="#22c55e"
          />
        </div>

        <div className="charts-grid">
          <div className="chart-card">
            <h3>Employees by Department</h3>

            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="employees" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Risk Distribution</h3>

            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  outerRadius={90}
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={index}
                      fill={COLORS[index]}
                    />
                  ))}
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;