import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth, ROLE_LABEL } from '../context/AuthContext';
import './AppShell.css';

// The name of each role's home screen, shown in the breadcrumb + header.
const WORKSPACE = {
  security_analyst: 'Analyst Workspace',
  soc_engineer: 'SOC Operations',
  security_manager: 'Command View',
  administrator: 'Administration',
};

// Nav items. `to` is the route; `roles` (optional) limits who sees it.
const NAV = [
  { to: '/', label: 'Overview', glyph: '◆', end: true },
  { to: '/alerts', label: 'Alert Queue', glyph: '▲' },
  { to: '/investigations', label: 'Investigations', glyph: '◎' },
  { to: '/employees', label: 'Employees', glyph: '⬡' },
  { to: '/entity', label: 'Entity Analytics', glyph: '◈' },
  { to: '/audit', label: 'Audit Log', glyph: '⧉', roles: ['administrator'] },
];

// Human label for the current route, for the breadcrumb.
const ROUTE_LABEL = {
  '/': 'Overview', '/alerts': 'Alert Queue', '/investigations': 'Investigations',
  '/employees': 'Employees', '/entity': 'Entity Analytics', '/audit': 'Audit Log',
};

export default function AppShell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const initials = (user?.full_name || user?.email || '?')
    .split(/[\s@._]/).filter(Boolean).slice(0, 2)
    .map((s) => s[0]?.toUpperCase()).join('');

  const visibleNav = NAV.filter((n) => !n.roles || n.roles.includes(user?.role));
  // current route label (match longest prefix)
  const crumb = ROUTE_LABEL[location.pathname]
    || (location.pathname.startsWith('/investigations') ? 'Investigations' : 'Overview');

  return (
    <div className="shell">
      <aside className="shell__nav">
        <div className="shell__brand">
          <span className="shell__brand-glyph" />
          <span className="shell__brand-text">ITBIS</span>
        </div>

        <nav className="shell__navlist">
          {visibleNav.map((item, i) => (
            <motion.div key={item.to}
              initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.04 * i, duration: 0.3 }}>
              <NavLink to={item.to} end={item.end}
                className={({ isActive }) => `navitem ${isActive ? 'navitem--active' : ''}`}>
                <span className="navitem__glyph">{item.glyph}</span>
                <span className="navitem__label">{item.label}</span>
              </NavLink>
            </motion.div>
          ))}
        </nav>

        <div className="shell__navfoot">
          <div className="shell__status">
            <span className="shell__status-dot" />
            <span className="mono">SYSTEM NOMINAL</span>
          </div>
        </div>
      </aside>

      <div className="shell__body">
        <header className="shell__top">
          <div className="shell__crumbs">
            <span className="eyebrow">{WORKSPACE[user?.role] || 'Console'}</span>
            <span className="shell__crumb-sep">/</span>
            <span className="shell__crumb-current">{crumb}</span>
          </div>

          <div className="shell__user">
            <div className="shell__user-meta">
              <div className="shell__user-name">{user?.full_name || user?.email}</div>
              <div className="shell__user-role">{ROLE_LABEL[user?.role] || user?.role}</div>
            </div>
            <div className="shell__avatar">{initials}</div>
            <button className="shell__logout" onClick={logout} title="Sign out">⏻</button>
          </div>
        </header>

        <main className="shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
