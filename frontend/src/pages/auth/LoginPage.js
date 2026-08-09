import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { apiError } from '../../utils/helpers';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();

  const [form,    setForm]    = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');
  const [showPw,  setShowPw]  = useState(false);

  const handle = async e => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  };

  const fill = (email, password) => setForm({ email, password });

  return (
    <div style={{
      minHeight: '100vh', background: 'var(--bg-base)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24,
    }}>
      {/* Background grid */}
      <div style={{
        position: 'fixed', inset: 0, opacity: 0.03,
        backgroundImage: 'linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)',
        backgroundSize: '40px 40px',
        pointerEvents: 'none',
      }} />

      <div style={{ width: '100%', maxWidth: 400, position: 'relative' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            width: 52, height: 52, borderRadius: 14,
            background: 'linear-gradient(135deg, var(--accent), #7c3aed)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 14px',
            boxShadow: '0 8px 24px rgba(45,126,247,0.3)',
          }}>
            <Shield size={26} color="#fff" />
          </div>
          <h1 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Insider Threat Intelligence
          </h1>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Behavioral Intelligence System
          </p>
        </div>

        {/* Card */}
        <div className="card" style={{ padding: 28 }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 20 }}>Sign in to your account</h2>

          {error && (
            <div style={{
              background: 'var(--risk-critical-bg)', border: '1px solid var(--risk-critical)',
              borderRadius: 8, padding: '10px 14px', marginBottom: 16,
              display: 'flex', gap: 8, alignItems: 'center',
            }}>
              <AlertCircle size={14} color="var(--risk-critical)" />
              <span style={{ fontSize: '0.82rem', color: 'var(--risk-critical)' }}>{error}</span>
            </div>
          )}

          <form onSubmit={handle}>
            <div className="form-group">
              <label className="form-label">Email address</label>
              <input className="form-input" type="email" placeholder="analyst@company.com"
                value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                required autoFocus />
            </div>

            <div className="form-group" style={{ position: 'relative' }}>
              <label className="form-label">Password</label>
              <input className="form-input" type={showPw ? 'text' : 'password'}
                placeholder="••••••••" value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                required style={{ paddingRight: 40 }} />
              <button type="button" onClick={() => setShowPw(v => !v)} style={{
                position: 'absolute', right: 10, top: 32,
                color: 'var(--text-muted)',
              }}>
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>

            <button type="submit" className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '10px', marginTop: 4 }}
              disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>

            <button type="button" className="btn btn-secondary"
              onClick={async () => {
                setLoading(true); setError('');
                try {
                  await login('analyst@company.com', 'Analyst123!');
                  navigate('/dashboard');
                } catch (err) {
                  setError(apiError(err));
                } finally {
                  setLoading(false);
                }
              }}
              style={{
                width: '100%', justifyContent: 'center', padding: '10px', marginTop: 10,
                border: '1px dashed var(--accent)', color: 'var(--accent)',
                background: 'rgba(45,126,247,0.05)'
              }}
              disabled={loading}>
              ⚡ One-Click Demo Sign In (Analyst)
            </button>
          </form>

          {/* Quick fill */}
          <div style={{ marginTop: 20, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8 }}>Demo accounts:</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {[
                ['Administrator', 'admin@company.com', 'Admin123!'],
                ['Manager',       'manager@company.com','Manager123!'],
                ['Analyst',       'analyst@company.com','Analyst123!'],
                ['SOC Engineer',  'soc@company.com',    'SOC123!pwd'],
              ].map(([label, email, pw]) => (
                <button key={label} onClick={() => fill(email, pw)}
                  className="btn btn-ghost"
                  style={{ fontSize: '0.72rem', padding: '4px 10px' }}>
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
