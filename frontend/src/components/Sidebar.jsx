import { Link, useLocation, useNavigate } from "react-router-dom";
import "../styles/Sidebar.css";

function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="sidebar">
      <h1>Insider Threat</h1>

      <Link
        to="/dashboard"
        className={location.pathname === "/dashboard" ? "active" : ""}
      >
        🏠 Dashboard
      </Link>

      <Link
        to="/employees"
        className={location.pathname === "/employees" ? "active" : ""}
      >
        👥 Employees
      </Link>

      <Link
        to="/predictions"
        className={location.pathname === "/predictions" ? "active" : ""}
      >
        🤖 Predictions
      </Link>

      <button className="logout-btn" onClick={logout}>
        🚪 Logout
      </button>
    </div>
  );
}

export default Sidebar;