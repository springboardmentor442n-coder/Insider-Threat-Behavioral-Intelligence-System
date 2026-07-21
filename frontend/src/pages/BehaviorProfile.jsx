import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import Sidebar from "../components/Sidebar";

export default function BehaviorProfile() {
  const [profiles, setProfiles] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadProfiles();
  }, []);

  async function loadProfiles() {
    try {
      const res = await axios.get("http://127.0.0.1:8000/behavior");
      setProfiles(res.data);
    } catch (err) {
      console.log(err);
    }
  }

  const filteredProfiles = profiles.filter((profile) =>
    profile.employee_id.toLowerCase().includes(search.toLowerCase())
  );

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
        <h1>Behavior Profiles</h1>

        <input
          type="text"
          placeholder="Search Employee..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            margin: "25px 0",
            padding: "10px",
            width: "260px",
            borderRadius: "8px",
            border: "none",
          }}
        />

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
              <th>Avg Login</th>
              <th>Avg Devices</th>
              <th>Avg Hour</th>
              <th>Weekend</th>
              <th>Risk Score</th>
              <th>Behavior Score</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredProfiles.map((profile) => (
              <tr
                key={profile.employee_id}
                style={{
                  textAlign: "center",
                  borderBottom: "1px solid #334155",
                }}
              >
                <td style={{ padding: "12px" }}>
                  <Link
                    to={`/employee/${profile.employee_id}`}
                    style={{
                      color: "#38bdf8",
                      textDecoration: "none",
                      fontWeight: "bold",
                    }}
                  >
                    {profile.employee_id}
                  </Link>
                </td>

                <td>{profile.department}</td>

                <td>{profile.avg_login}</td>

                <td>{profile.avg_devices}</td>

                <td>{profile.avg_hour}</td>

                <td>
                  {profile.weekend_activity ? "Yes" : "No"}
                </td>

                <td>
                  <span
                    style={{
                      color:
                        profile.risk_score >= 80
                          ? "#ef4444"
                          : profile.risk_score >= 50
                          ? "#f59e0b"
                          : "#22c55e",
                      fontWeight: "bold",
                    }}
                  >
                    {profile.risk_score}
                  </span>
                </td>

                <td>{profile.behavior_score}</td>

                <td>
                  <span
                    style={{
                      padding: "6px 12px",
                      borderRadius: "20px",
                      color: "white",
                      background:
                        profile.status === "Critical"
                          ? "#dc2626"
                          : profile.status === "High"
                          ? "#ea580c"
                          : profile.status === "Medium"
                          ? "#ca8a04"
                          : "#16a34a",
                    }}
                  >
                    {profile.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredProfiles.length === 0 && (
          <div
            style={{
              marginTop: "40px",
              textAlign: "center",
              color: "#94a3b8",
            }}
          >
            No behavior profiles available.
          </div>
        )}
      </div>
    </div>
  );
}