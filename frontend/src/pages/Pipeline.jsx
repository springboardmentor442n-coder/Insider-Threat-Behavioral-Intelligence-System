import { useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import "../styles/Pipeline.css";

export default function Pipeline() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const [lastRun, setLastRun] = useState("");

  const runPipeline = async () => {
    if (!file) {
      setMessage("Please select a CSV file.");
      setIsSuccess(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setMessage("");
      setResult(null);

      const response = await axios.post(
        "http://127.0.0.1:8000/run-pipeline",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);

      setMessage("✅ Threat Detection Completed Successfully!. Results have been saved to the database.");
      setIsSuccess(true);

      setLastRun(new Date().toLocaleString());
    } catch (err) {
      console.error(err);

      setMessage(
        "❌ Threat Detection Failed. Please verify the uploaded CSV file and try again."
      );

      setIsSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pipeline-container">
      <Sidebar />

      <div className="pipeline-content">
        <h1>Insider Threat Detection Pipeline</h1>

        <p>
          Upload a CERT log dataset to detect potential insider threats
          using Machine Learning.
        </p>

        <div className="upload-box">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {file && (
            <p style={{ marginTop: "15px", color: "#38bdf8" }}>
              <strong>Selected File:</strong> {file.name}
            </p>
          )}

          <br />

          <button
            className="run-btn"
            onClick={runPipeline}
            disabled={loading}
          >
            {loading
              ? "🔍 Detecting Insider Threats..."
              : "🚀 Run Threat Detection"}
          </button>
        </div>

        {message && (
          <div
            className={
              isSuccess ? "success-message" : "error-message"
            }
          >
            {message}
          </div>
        )}

        {result && (
          <>
            <div className="result-grid">
              <div className="result-card">
                <h2>📄 Rows Processed</h2>
                <p>{Number(result.rows_processed).toLocaleString()}</p>
              </div>

              <div className="result-card">
                <h2>🚨 High Risk</h2>
                <p>{Number(result.high_risk).toLocaleString()}</p>
              </div>

              <div className="result-card">
                <h2>✅ Low Risk</h2>
                <p>{Number(result.low_risk).toLocaleString()}</p>
              </div>

              <div className="result-card">
                <h2>💾 Saved to Database</h2>
                <p>{Number(result.saved_to_database).toLocaleString()}</p>
              </div>
            </div>

            {lastRun && (
              <div
                style={{
                  marginTop: "30px",
                  textAlign: "center",
                  color: "#94a3b8",
                  fontSize: "16px",
                }}
              >
                <strong>🕒 Last Pipeline Run:</strong> {lastRun}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}