import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, Activity, AlertTriangle,
  Shield, Bell, FileText, LogOut,
  Radar, Brain, Cpu, Network,
  TrendingUp, Target, Settings, FlaskConical,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ROLE_LABELS } from '../../utils/helpers';
import toast from 'react-hot-toast';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'SOC Dashboard', color: '#00d4ff' },
    ],
  },
  {
    label: 'Monitoring',
    items: [
      { to: '/employees',  icon: Users,     label: 'Employees',      color: '#8b5cf6' },
      { to: '/activities', icon: Activity,  label: 'Activity Logs',  color: '#10b981' },
      { to: '/anomalies',  icon: Radar,     label: 'Anomalies',      color: '#f59e0b' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { to: '/risk',       icon: Shield,       label: 'Risk Scores',    color: '#f43f5e' },
      { to: '/ml',         icon: Brain,        label: 'ML Inference',   color: '#6366f1' },
      { to: '/ueba',       icon: Network,      label: 'UEBA Analytics', color: '#14b8a6' },
      { to: '/predict',    icon: FlaskConical, label: 'Prediction Lab', color: '#a78bfa' },
    ],
  },
  {
    label: 'Management',
    items: [
      { to: '/alerts',    icon: Bell,          label: 'Alerts',         color: '#f97316' },
      { to: '/incidents', icon: AlertTriangle, label: 'Incidents',      color: '#ec4899' },
      { to: '/reports',   icon: FileText,      label: 'Reports',        color: '#84cc16' },
    ],
  },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Logged out');
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #00d4ff 0%, #6366f1 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0, boxShadow: '0 0 16px rgba(0,212,255,0.4)',
          }}>
            <Shield size={18} color="#fff" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-brand)',
              fontSize: '0.88rem',
              fontWeight: 900,
              color: '#fff',
              letterSpacing: '0.05em',
              lineHeight: 1.2,
            }}>
              ITBIS
            </div>
            <div style={{ fontSize: '0.62rem', color: 'rgba(0,212,255,0.7)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Threat Intelligence
            </div>
          </div>
        </div>

        {/* System status indicator */}
        <div style={{
          marginTop: 12,
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '6px 10px',
          borderRadius: 8,
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.18)',
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#10b981',
            boxShadow: '0 0 6px #10b981',
            animation: 'pulse-ring 2s infinite',
          }} />
          <span style={{ fontSize: '0.68rem', color: '#34d399', fontWeight: 600 }}>SYSTEM OPERATIONAL</span>
        </div>
      </div>

      {/* Nav groups */}
      <nav style={{ flex: 1, padding: '8px 0', overflowY: 'auto' }}>
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <div className="sidebar-nav-group-label">{group.label}</div>
            {group.items.map(({ to, icon: Icon, label, color }) => (
              <NavLink key={to} to={to} className={({ isActive }) =>
                `sidebar-nav-item${isActive ? ' active' : ''}`
              } style={({ isActive }) => ({
                '--nav-color': color,
                background: isActive ? `${color}12` : 'transparent',
              })}>
                {({ isActive }) => (
                  <>
                    <div style={{
                      width: 28, height: 28, borderRadius: 7,
                      background: isActive ? `${color}20` : 'transparent',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0, transition: 'all 0.2s',
                    }}>
                      <Icon size={14} color={isActive ? color : 'var(--text-muted)'} strokeWidth={2} />
                    </div>
                    <span style={{ flex: 1, color: isActive ? color : 'var(--text-secondary)' }}>{label}</span>
                    {isActive && (
                      <div style={{ width: 4, height: 4, borderRadius: '50%', background: color, opacity: 0.8 }} />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Bottom section */}
      <div style={{ padding: '10px 8px 14px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <NavLink to="/settings" className="sidebar-nav-item" style={{ marginBottom: 4 }}>
          <div style={{ width: 28, height: 28, borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Settings size={14} color="var(--text-muted)" />
          </div>
          <span>Settings</span>
        </NavLink>

        {/* User card */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '10px 12px', borderRadius: 10,
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.06)',
          marginTop: 6,
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'linear-gradient(135deg, #00d4ff, #6366f1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.75rem', fontWeight: 800, color: '#fff', flexShrink: 0,
            boxShadow: '0 0 10px rgba(0,212,255,0.3)',
          }}>
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="truncate" style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {user?.full_name}
            </div>
            <div style={{
              fontSize: '0.62rem',
              color: '#00d4ff',
              fontWeight: 600,
              letterSpacing: '0.05em',
            }}>
              {ROLE_LABELS[user?.role] || user?.role}
            </div>
          </div>
          <button onClick={handleLogout} title="Logout" style={{
            color: 'var(--text-muted)', padding: 5, borderRadius: 6,
            background: 'transparent', border: 'none', cursor: 'pointer',
            transition: 'all 0.15s',
          }}
            onMouseEnter={e => e.currentTarget.style.color = '#f43f5e'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <LogOut size={13} />
          </button>
        </div>
      </div>
    </aside>
  );
}
