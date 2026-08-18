function Sidebar({ currentRoute, setCurrentRoute }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">INSIGHTGUARD</h2>
        <p className="sidebar-subtitle">Behavioral Intelligence</p>
      </div>
      
      <nav className="sidebar-nav">
        <a 
          className={`nav-item ${currentRoute === 'Overview' ? 'active' : ''}`}
          onClick={() => setCurrentRoute('Overview')}
        >
          Overview
        </a>
        <a 
          className={`nav-item ${currentRoute === 'Employees' ? 'active' : ''}`}
          onClick={() => setCurrentRoute('Employees')}
        >
          Employees
        </a>
        <a 
          className={`nav-item ${currentRoute === 'BehaviorAnalysis' ? 'active' : ''}`}
          onClick={() => setCurrentRoute('BehaviorAnalysis')}
        >
          Behavior Analysis
        </a>
        <a 
          className={`nav-item ${currentRoute === 'BatchAnalysis' ? 'active' : ''}`}
          onClick={() => setCurrentRoute('BatchAnalysis')}
        >
          Batch Analysis
        </a>
        <a 
          className={`nav-item ${currentRoute === 'PredictionHistory' ? 'active' : ''}`}
          onClick={() => setCurrentRoute('PredictionHistory')}
        >
          Prediction History
        </a>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-title">
          Model Intelligence
        </div>
        <div className="sidebar-footer-item">
          <span className="status-dot"></span> API Connected
        </div>
        <div className="sidebar-footer-item">
          <span className="status-dot"></span> Model Ready
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

