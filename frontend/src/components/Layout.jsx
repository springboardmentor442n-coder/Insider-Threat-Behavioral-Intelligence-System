import React, { useContext, useState } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ThemeContext } from '../context/ThemeContext';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Users, 
  Activity, 
  Cpu, 
  Bell, 
  FileSearch, 
  FileText, 
  Settings, 
  LogOut,
  Sun,
  Moon,
  Search,
  ChevronRight,
  Flame,
  Upload,
  HelpCircle,
  Layers
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useContext(AuthContext);
  const { theme, toggleTheme } = useContext(ThemeContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [globalSearch, setGlobalSearch] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/threat-center', label: 'Threat Center', icon: Flame },
    { path: '/employees', label: 'Employees', icon: Users },
    { path: '/upload-analyze', label: 'Upload & Analyze', icon: Upload },
    { path: '/investigations', label: 'Investigation', icon: FileSearch },
    { path: '/alerts', label: 'Alerts', icon: Bell },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];


  const getBreadcrumb = () => {
    const active = navItems.find(item => item.path === location.pathname);
    if (active) return active.label;
    if (location.pathname.startsWith('/users/') || location.pathname.startsWith('/employees/')) {
      const parts = location.pathname.split('/');
      return `Employee Details: ${parts[2] || 'Profile'}`;
    }
    return 'Console';
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (globalSearch.trim()) {
      navigate(`/employees?search=${encodeURIComponent(globalSearch.trim())}`);
      setGlobalSearch('');
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar Navigation */}
      <aside style={{
        width: '250px',
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        bottom: 0,
        left: 0,
        zIndex: 100
      }}>
        {/* Logo Banner */}
        <div style={{
          padding: '18px 20px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
            padding: '8px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px rgba(56, 189, 248, 0.4)'
          }}>
            <ShieldAlert size={20} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '0.9rem', fontWeight: 800, letterSpacing: '-0.3px', color: 'var(--text-main)' }}>INSIDER THREAT</h1>
            <p style={{ fontSize: '0.62rem', color: 'var(--accent-cyan)', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase' }}>Security Console</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: '14px 10px', overflowY: 'auto' }}>
          <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-dim)', fontWeight: 700, padding: '0 10px 6px 10px', letterSpacing: '1px' }}>
            SOC Console Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '9px 12px',
                  borderRadius: '7px',
                  color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                  backgroundColor: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                  borderLeft: isActive ? '3px solid var(--accent-cyan)' : '3px solid transparent',
                  fontWeight: isActive ? 600 : 400,
                  fontSize: '0.84rem',
                  marginBottom: '2px',
                  transition: 'all 0.2s ease'
                })}
              >
                <Icon size={17} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* User Footer */}
        <div style={{
          padding: '14px 16px',
          borderTop: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-card)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px', fontSize: '0.7rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--accent-emerald)', boxShadow: '0 0 6px var(--accent-emerald)' }}></span>
            <span>GB ML Model Active</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: 'rgba(56, 189, 248, 0.2)',
                border: '1px solid var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-cyan)',
                fontWeight: 700,
                fontSize: '0.8rem'
              }}>
                {user?.username?.substring(0, 2).toUpperCase() || 'SA'}
              </div>
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>{user?.username || 'Analyst'}</div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>SOC Analyst</div>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              title="Logout"
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', padding: '4px' }}
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Header & Body */}
      <div style={{
        flex: 1,
        marginLeft: '250px',
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        maxWidth: 'calc(100vw - 250px)'
      }}>
        <header style={{
          height: '60px',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 32px',
          position: 'sticky',
          top: 0,
          zIndex: 90
        }}>
          <div className="breadcrumb">
            <span>Security Console</span>
            <ChevronRight size={14} />
            <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{getBreadcrumb()}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <form onSubmit={handleSearchSubmit} style={{ position: 'relative', width: '240px' }}>
              <Search size={15} style={{ position: 'absolute', left: '10px', top: '9px', color: 'var(--text-dim)' }} />
              <input
                type="text"
                className="input-field"
                placeholder="Search user ID (e.g. USR0017)..."
                style={{ paddingLeft: '32px', paddingRight: '10px', fontSize: '0.8rem', height: '32px' }}
                value={globalSearch}
                onChange={(e) => setGlobalSearch(e.target.value)}
              />
            </form>

            <button onClick={toggleTheme} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem', height: '32px' }}>
              {theme === 'dark' ? <Sun size={15} color="var(--accent-amber)" /> : <Moon size={15} color="var(--accent-purple)" />}
              <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>

            <button onClick={() => navigate('/alerts')} style={{ position: 'relative', background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '7px', borderRadius: '7px', cursor: 'pointer' }}>
              <Bell size={17} />
            </button>
          </div>
        </header>

        <main style={{ flex: 1, padding: '28px 32px' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
