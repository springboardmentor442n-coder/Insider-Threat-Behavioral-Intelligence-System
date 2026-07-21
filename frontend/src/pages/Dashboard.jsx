import { useEffect, useState } from "react";
import axios from "axios";
import Layout from "../components/Layout";

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

  const cardStyle = {
    background: "#1e293b",
    padding: "25px",
    borderRadius: "12px",
    textAlign: "center",
    boxShadow: "0 0 10px rgba(0,0,0,.3)",
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "20px",
  };

  return (
    <Layout title="Dashboard">

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(5,1fr)",
          gap: "20px",
          marginBottom: "40px",
        }}
      >

        <div style={cardStyle}>
          <h3>Employees</h3>
          <h1>{stats.total_employees}</h1>
        </div>

        <div style={cardStyle}>
          <h3>Predictions</h3>
          <h1>{stats.total_predictions}</h1>
        </div>

        <div style={cardStyle}>
          <h3>High Risk</h3>
          <h1 style={{color:"red"}}>{stats.high_risk}</h1>
        </div>

        <div style={cardStyle}>
          <h3>Safe Users</h3>
          <h1 style={{color:"#22c55e"}}>{stats.low_risk}</h1>
        </div>

        <div style={cardStyle}>
          <h3>Avg Confidence</h3>
          <h1>{stats.average_confidence?.toFixed(1)}%</h1>
        </div>

      </div>

      <h2>Top Risk Employees</h2>

      <table style={tableStyle}>

        <thead style={{background:"#1e293b"}}>

          <tr>

            <th>Employee</th>
            <th>Department</th>
            <th>Risk Score</th>
            <th>Status</th>

          </tr>

        </thead>

        <tbody>

          {topRisk.map(emp=>(

            <tr
              key={emp.employee_id}
              style={{
                textAlign:"center",
                borderBottom:"1px solid #334155"
              }}
            >

              <td>{emp.employee_id}</td>

              <td>{emp.department}</td>

              <td>{emp.risk_score}</td>

              <td>

                <span
                  style={{
                    color:
                      emp.status==="Critical"
                      ?"red"
                      :emp.status==="High"
                      ?"orange"
                      :"#22c55e",

                    fontWeight:"bold"
                  }}
                >

                  {emp.status}

                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

      <br/><br/>

      <h2>Recent Alerts</h2>

      <table style={tableStyle}>

        <thead style={{background:"#1e293b"}}>

          <tr>

            <th>Employee</th>

            <th>Department</th>

            <th>Risk</th>

            <th>Confidence</th>

          </tr>

        </thead>

        <tbody>

          {alerts.map(alert=>(

            <tr
              key={alert.employee_id}
              style={{
                textAlign:"center",
                borderBottom:"1px solid #334155"
              }}
            >

              <td>{alert.employee_id}</td>

              <td>{alert.department}</td>

              <td style={{color:"red"}}>

                {alert.risk_level}

              </td>

              <td>

                {alert.confidence.toFixed(2)}%

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </Layout>
  );
}