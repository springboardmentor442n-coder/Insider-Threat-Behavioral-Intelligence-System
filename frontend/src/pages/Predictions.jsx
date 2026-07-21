import { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";

export default function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");

  useEffect(() => {
    loadPredictions();
  }, []);

  async function loadPredictions() {
    try {
      const res = await axios.get("http://127.0.0.1:8000/predictions");
      setPredictions(res.data);
      setFiltered(res.data);
    } catch (err) {
      console.log(err);
    }
  }

  useEffect(() => {
    let data = [...predictions];

    if (search !== "") {
      data = data.filter((item) =>
        item.employee_id.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (riskFilter !== "ALL") {
      data = data.filter((item) => item.risk_level === riskFilter);
    }

    setFiltered(data);
  }, [search, riskFilter, predictions]);

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <Sidebar />

      <div
        style={{
          flex: 1,
          padding: "40px",
          color: "white",
        }}
      >
        <h1>Threat Predictions</h1>

        <div
          style={{
            display: "flex",
            gap: "15px",
            margin: "25px 0",
          }}
        >
          <input
            type="text"
            placeholder="Search Employee..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              padding: "10px",
              width: "250px",
              borderRadius: "8px",
              border: "none",
            }}
          />

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "none",
            }}
          >
            <option value="ALL">All</option>
            <option value="HIGH">High</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "#1e293b",
            borderRadius: "10px",
            overflow: "hidden",
          }}
        >
          <thead>
            <tr style={{ background: "#334155" }}>
              <th style={{ padding: "15px" }}>Employee</th>
              <th>Department</th>
              <th>Login Count</th>
              <th>Devices</th>
              <th>Hour</th>
              <th>Risk</th>
              <th>Confidence</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((item) => (
              <tr
                key={item.prediction_id}
                style={{
                  textAlign: "center",
                  borderBottom: "1px solid #334155",
                }}
              >
                <td style={{ padding: "12px" }}>{item.employee_id}</td>

                <td>{item.department}</td>

                <td>{item.login_count}</td>

                <td>{item.unique_pc_count}</td>

                <td>{item.hour}:00</td>

                <td>
                  <span
                    style={{
                      color:
                        item.risk_level === "HIGH"
                          ? "#ef4444"
                          : "#22c55e",
                      fontWeight: "bold",
                    }}
                  >
                    {item.risk_level}
                  </span>
                </td>

                <td>{Number(item.confidence).toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}