import { Bell, Search, Shield, Cpu, Clock, Wifi } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useState, useEffect } from 'react';

export default function Topbar({ title, subtitle }) {
  const { user } = useAuth();
  const [time, setTime] = useState(new Date());
  const [alerts] = useState(3);

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeStr = time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const dateStr = time.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  return (
    <header className="topbar">
      {/* Left: Page title */}
      <div style={{ flex: 1 }}>
        {title && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <h1 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{title}</h1>
            </div>
            {subtitle && (
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 1 }}>{subtitle}</p>
            )}
          </div>
        )}
      </div>

      {/* Center: Live threat indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '5px 12px', borderRadius: 999,
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#10b981', boxShadow: '0 0 6px #10b981',
            animation: 'pulse-ring 2s infinite',
          }} />
          <span style={{ fontSize: '0.68rem', color: '#34d399', fontWeight: 700, letterSpacing: '0.08em' }}>LIVE</span>
        </div>

        <div style={{
          display: 'flex', alignItems: 'center', gap: 5,
          padding: '5px 12px', borderRadius: 999,
          background: 'rgba(0,212,255,0.06)',
          border: '1px solid rgba(0,212,255,0.15)',
        }}>
          <Wifi size={11} color="var(--accent)" />
          <span style={{ fontSize: '0.68rem', color: 'var(--accent)', fontWeight: 600 }}>MONITORING</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* Clock */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '5px 10px', borderRadius: 8,
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid var(--border)',
        }}>
          <Clock size={11} color="var(--text-muted)" />
          <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            {timeStr}
          </span>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{dateStr}</span>
        </div>

        {/* Notifications */}
        <button style={{
          width: 34, height: 34, borderRadius: 8,
          background: 'rgba(255,255,255,0.05)',
          border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-secondary)', position: 'relative', cursor: 'pointer',
          transition: 'all 0.2s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(244,63,94,0.1)'; e.currentTarget.style.borderColor = 'rgba(244,63,94,0.3)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
        >
          <Bell size={14} />
          {alerts > 0 && (
            <span className="notif-badge">{alerts}</span>
          )}
        </button>

        {/* User avatar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '5px 10px', borderRadius: 8,
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid var(--border)',
          cursor: 'pointer',
        }}>
          <div style={{
            width: 26, height: 26, borderRadius: '50%',
            background: 'linear-gradient(135deg, #00d4ff, #6366f1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.72rem', fontWeight: 800, color: '#fff',
          }}>
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              {user?.full_name?.split(' ')[0]}
            </div>
            <div style={{ fontSize: '0.62rem', color: '#00d4ff', fontWeight: 600 }}>
              {user?.role}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
