import { useState } from "react";
import Login from "./components/Login";
import Sidebar from "./components/Sidebar";
import Overview from "./components/Overview";
import BehaviorAnalysis from "./components/BehaviorAnalysis";
import Employees from "./components/Employees";
import PredictionHistory from "./components/PredictionHistory";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return sessionStorage.getItem("insightguard_auth") === "true";
  });
  const [currentRoute, setCurrentRoute] = useState("Overview");
  const [recentAnalyses, setRecentAnalyses] = useState(() => {
    const user = sessionStorage.getItem("insightguard_user") || "default";
    let savedLocal = localStorage.getItem(`insightguard_data_${user}`);
    return savedLocal ? JSON.parse(savedLocal) : [];
  });

  const [selectedEmployee, setSelectedEmployee] = useState("");

  const updateRecentAnalyses = (newAnalyses) => {
    const user = sessionStorage.getItem("insightguard_user") || "default";
    if (typeof newAnalyses === 'function') {
      setRecentAnalyses(prev => {
        const updated = newAnalyses(prev);
        localStorage.setItem(`insightguard_data_${user}`, JSON.stringify(updated));
        return updated;
      });
    } else {
      setRecentAnalyses(newAnalyses);
      localStorage.setItem(`insightguard_data_${user}`, JSON.stringify(newAnalyses));
    }
  };

  const handleLogin = (email) => {
    sessionStorage.setItem("insightguard_auth", "true");
    if (email) sessionStorage.setItem("insightguard_user", email);
    
    const user = email || "default";
    let savedLocal = localStorage.getItem(`insightguard_data_${user}`);
    setRecentAnalyses(savedLocal ? JSON.parse(savedLocal) : []);
    
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    sessionStorage.removeItem("insightguard_auth");
    sessionStorage.removeItem("insightguard_user");
    setIsLoggedIn(false);
    setRecentAnalyses([]);
    setCurrentRoute("Overview");
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  const renderContent = () => {
    switch (currentRoute) {
      case "Overview":
        return <Overview setCurrentRoute={setCurrentRoute} recentAnalyses={recentAnalyses} />;
      case "Employees":
        return <Employees setCurrentRoute={setCurrentRoute} recentAnalyses={recentAnalyses} setSelectedEmployee={setSelectedEmployee} />;
      case "BehaviorAnalysis":
        return <BehaviorAnalysis recentAnalyses={recentAnalyses} setRecentAnalyses={updateRecentAnalyses} selectedEmployee={selectedEmployee} setSelectedEmployee={setSelectedEmployee} />;
      case "PredictionHistory":
        return <PredictionHistory recentAnalyses={recentAnalyses} setRecentAnalyses={updateRecentAnalyses} />;
      default:
        return <Overview setCurrentRoute={setCurrentRoute} recentAnalyses={recentAnalyses} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar currentRoute={currentRoute} setCurrentRoute={setCurrentRoute} />
      
      <main className="main-content">
        <header className="top-header">
          <div className="header-left">
            <span style={{ color: "var(--text-primary)", fontWeight: 600, marginRight: "0.5rem" }}>Security Operations</span>
            <span style={{ color: "var(--border-color)", margin: "0 0.5rem" }}>/</span>
            <span style={{ color: "var(--accent-secondary)" }}>Behavioral Intelligence Monitoring</span>
          </div>
          <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>
              <span className="status-dot"></span>
              {sessionStorage.getItem("insightguard_user") || "Analyst"}
            </span>
            <span>System Status: <span style={{ color: "var(--accent-primary)", marginLeft: "0.25rem" }}>Operational</span></span>
            <button 
              onClick={handleLogout} 
              style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.25rem 0.75rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' }}
            >
              Logout
            </button>
          </div>
        </header>
        
        <div className="content-area">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;