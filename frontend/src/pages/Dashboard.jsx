import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
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

const pieData = [
  { name: "Safe", value: 242 },
  { name: "Risk", value: 8 },
];

const barData = [
  { department: "HR", employees: 40 },
  { department: "Finance", employees: 60 },
  { department: "IT", employees: 90 },
  { department: "Sales", employees: 60 },
];

const COLORS = ["#4ade80", "#f97316"];

function Dashboard() {
  return (
    <div className="dashboard-layout">
      <Sidebar />

      <div className="dashboard-content">
        <h1>Dashboard</h1>
        <p>Insider Threat Behavioral Intelligence System</p>

        <div className="stats-grid">
          <StatCard title="Employees" value="250" color="#67e8f9" />
          <StatCard title="Threat Alerts" value="12" color="#f59e0b" />
          <StatCard title="Risk Users" value="8" color="#facc15" />
          <StatCard title="Safe Users" value="242" color="#4ade80" />
        </div>

        <div className="charts-grid">

          <div className="chart-card">
            <h3>Employees by Department</h3>

            <ResponsiveContainer width="100%" height={280}>
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