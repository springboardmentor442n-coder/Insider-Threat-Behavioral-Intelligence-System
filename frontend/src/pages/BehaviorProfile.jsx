import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { getBehaviorProfiles } from "../services/behaviorService";
import "../styles/BehaviorProfile.css";
import "../styles/Dashboard.css";

function BehaviorProfile() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const data = await getBehaviorProfiles();
        setProfiles(data);
      } catch (error) {
        console.error("Error fetching behavior profiles:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, []);

  return (
    <div className="dashboard-layout">
      <Sidebar />

      <div className="dashboard-content">
        <h1>Behavior Profiles</h1>
        <p>Employee Behavioral Analysis</p>

        {loading ? (
          <h3>Loading...</h3>
        ) : (
          <table className="behavior-table">
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Behavior Score</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {profiles.map((employee) => (
                <tr key={employee.employee_id}>
                  <td>{employee.employee_id}</td>
                  <td>{employee.name}</td>
                  <td>{employee.department}</td>
                  <td>{employee.behavior_score}</td>
                  <td>{employee.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default BehaviorProfile;