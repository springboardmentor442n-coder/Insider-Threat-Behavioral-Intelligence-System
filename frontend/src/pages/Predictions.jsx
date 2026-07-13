import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";

function Predictions() {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await api.get("/predictions");
      setPredictions(response.data);
    } catch (error) {
      console.error("Error fetching predictions:", error);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <Sidebar />

      <div style={{ flex: 1, padding: "40px", color: "white" }}>
        <h1>Threat Predictions</h1>

        <table
          style={{
            width: "100%",
            marginTop: "30px",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr style={{ background: "#1e293b" }}>
              <th style={{ padding: "15px" }}>ID</th>
              <th>Login Count</th>
              <th>Unique PCs</th>
              <th>Hour</th>
              <th>Weekend</th>
              <th>Risk</th>
              <th>Confidence</th>
            </tr>
          </thead>

          <tbody>
            {predictions.map((item) => (
              <tr
                key={item.id}
                style={{
                  textAlign: "center",
                  background: "#273549",
                  borderBottom: "8px solid #0f172a",
                }}
              >
                <td style={{ padding: "15px" }}>{item.id}</td>
                <td>{item.login_count}</td>
                <td>{item.unique_pc_count}</td>
                <td>{item.hour}</td>
                <td>{item.is_weekend ? "Yes" : "No"}</td>
                <td
                  style={{
                    color:
                      item.risk_level === "HIGH" ? "#ef4444" : "#4ade80",
                    fontWeight: "bold",
                  }}
                >
                  {item.risk_level}
                </td>
                <td>{item.confidence}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Predictions;