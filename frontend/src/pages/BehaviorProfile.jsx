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
                <th style={{ padding: "15px" }}>Employee ID</th>
                <th>Login Count</th>
                <th>Unique PCs</th>
                <th>Weekend Logins</th>
                <th>After Hours</th>
                <th>Average Login Hour</th>
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
                {profile.employee_id}
            </td>

            <td>{profile.login_count}</td>

            <td>{profile.unique_pc_count}</td>

            <td>{profile.weekend_logins}</td>

            <td>{profile.after_hours_logins}</td>

            <td>
                {Number(profile.average_login_hour).toFixed(2)}
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
