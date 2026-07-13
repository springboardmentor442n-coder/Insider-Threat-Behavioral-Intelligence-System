import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";

function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [employeeId, setEmployeeId] = useState("");
  const [loginCount, setLoginCount] = useState("");
  const [uniquePCCount, setUniquePCCount] = useState("");
  const [hour, setHour] = useState("");
  const [weekend, setWeekend] = useState(0);

  const [result, setResult] = useState(null);

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

  const handlePredict = async () => {
    if (
      employeeId === "" ||
      loginCount === "" ||
      uniquePCCount === "" ||
      hour === ""
    ) {
      alert("Please fill all fields.");
      return;
    }

    try {
      const response = await api.post("/predict", {
        employee_id: employeeId,
        login_count: Number(loginCount),
        unique_pc_count: Number(uniquePCCount),
        is_weekend: Number(weekend),
        hour: Number(hour),
      });

      setResult(response.data);
      setEmployeeId("");
      setLoginCount("");
      setUniquePCCount("");
      setHour("");
      setWeekend(0);

      fetchPredictions();
    } catch (error) {
      console.error(error);
      alert("Prediction failed.");
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

      <div
        style={{
          flex: 1,
          padding: "40px",
          color: "white",
        }}
      >
        <h1>Threat Prediction</h1>

        <div
          style={{
            background: "#1e293b",
            padding: "25px",
            borderRadius: "12px",
            marginTop: "25px",
            marginBottom: "30px",
          }}
        >
          <h2>Predict Insider Threat</h2>
          <input
            type="text"
            placeholder="Employee ID"
            value={employeeId}
            onChange={(e) => setEmployeeId(e.target.value)}
            style={inputStyle}
          />
          <input
            type="number"
            placeholder="Login Count"
            value={loginCount}
            onChange={(e) => setLoginCount(e.target.value)}
            style={inputStyle}
          />

          <input
            type="number"
            placeholder="Unique PC Count"
            value={uniquePCCount}
            onChange={(e) => setUniquePCCount(e.target.value)}
            style={inputStyle}
          />

          <input
            type="number"
            placeholder="Hour (0-23)"
            value={hour}
            onChange={(e) => setHour(e.target.value)}
            style={inputStyle}
          />

          <select
            value={weekend}
            onChange={(e) => setWeekend(e.target.value)}
            style={inputStyle}
          >
            <option value={0}>Weekday</option>
            <option value={1}>Weekend</option>
          </select>

          <button
            onClick={handlePredict}
            style={{
              marginTop: "15px",
              padding: "12px 25px",
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Predict
          </button>

          {result && (
            <div
              style={{
                marginTop: "25px",
                padding: "20px",
                background: "#273549",
                borderRadius: "10px",
              }}
            >
              <h3>Prediction Result</h3>

              <p>
                <strong>Risk Level:</strong>{" "}
                <span
                  style={{
                    color:
                      result.risk_level === "HIGH"
                        ? "#ef4444"
                        : "#22c55e",
                  }}
                >
                  {result.risk_level}
                </span>
              </p>

              <p>
                <strong>Confidence:</strong> {result.confidence}%
              </p>
            </div>
          )}
        </div>

        <h2>Prediction History</h2>

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "20px",
          }}
        >
          <thead>
            <tr style={{ background: "#1e293b" }}>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Login Count</th>
              <th style={thStyle}>Unique PCs</th>
              <th style={thStyle}>Hour</th>
              <th style={thStyle}>Weekend</th>
              <th style={thStyle}>Risk</th>
              <th style={thStyle}>Confidence</th>
            </tr>
          </thead>

          <tbody>
            {predictions.map((item) => (
              <tr
                key={item.id}
                style={{
                  background: "#273549",
                  textAlign: "center",
                }}
              >
                <td style={tdStyle}>{item.id}</td>
                <td style={tdStyle}>{item.login_count}</td>
                <td style={tdStyle}>{item.unique_pc_count}</td>
                <td style={tdStyle}>{item.hour}</td>
                <td style={tdStyle}>
                  {item.is_weekend ? "Yes" : "No"}
                </td>

                <td
                  style={{
                    ...tdStyle,
                    color:
                      item.risk_level === "HIGH"
                        ? "#ef4444"
                        : "#22c55e",
                    fontWeight: "bold",
                  }}
                >
                  {item.risk_level}
                </td>

                <td style={tdStyle}>{item.confidence}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const inputStyle = {
  display: "block",
  width: "300px",
  marginBottom: "15px",
  padding: "10px",
  borderRadius: "8px",
  border: "none",
  fontSize: "15px",
};

const thStyle = {
  padding: "15px",
};

const tdStyle = {
  padding: "15px",
};

export default Predictions;