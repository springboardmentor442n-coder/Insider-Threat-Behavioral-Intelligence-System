import React, { useState, useContext } from 'react';
import { ThemeContext } from '../context/ThemeContext';
import { AuthContext } from '../context/AuthContext';
import { Settings as SettingsIcon, ShieldCheck, Database, Cpu, Lock, User, Bell, Sun, Moon, Save, CheckCircle2 } from 'lucide-react';

const Settings = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('profile');
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Form states
  const [profileData, setProfileData] = useState({
    username: user?.username || 'analyst',
    email: 'analyst@cybersec.enterprise.org',
    role: user?.role || 'SOC Security Analyst',
    department: 'Cyber Threat Intelligence (CTI)'
  });

  const [securityData, setSecurityData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    mfaEnabled: true,
    sessionTimeoutMinutes: 30
  });

  const [notificationData, setNotificationData] = useState({
    emailAlerts: true,
    criticalOnly: true,
    slackWebhook: 'https://hooks.slack.com/services/T00/B00/XXXX',
    dailySummary: true
  });

  const handleSave = (e) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>System & Console Configuration</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Manage analyst profile, security settings, alert notifications, UI appearance, and ML engine parameters
        </p>
      </div>

      {/* Tabs */}
      <div className="glass-card" style={{ padding: '12px 20px', marginBottom: '24px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {[
          { id: 'profile', label: '1. Profile', icon: User },
          { id: 'security', label: '2. Security', icon: Lock },
          { id: 'notifications', label: '3. Notifications', icon: Bell },
          { id: 'appearance', label: '4. Appearance', icon: Sun },
          { id: 'ml_specs', label: '5. System & ML Spec', icon: Cpu }
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <Icon size={16} />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {savedSuccess && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--accent-emerald)', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
          <CheckCircle2 size={18} />
          <span>Configuration settings updated successfully!</span>
        </div>
      )}

      {/* Tab 1: Profile */}
      {activeTab === 'profile' && (
        <div className="glass-card" style={{ padding: '28px', maxWidth: '650px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px' }}>Analyst Profile Settings</h3>
          <form onSubmit={handleSave}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>USERNAME</label>
              <input
                type="text"
                className="input-field"
                value={profileData.username}
                onChange={(e) => setProfileData(p => ({ ...p, username: e.target.value }))}
                required
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>WORK EMAIL</label>
              <input
                type="email"
                className="input-field"
                value={profileData.email}
                onChange={(e) => setProfileData(p => ({ ...p, email: e.target.value }))}
                required
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>ANALYST ROLE</label>
                <input type="text" className="input-field" value={profileData.role} disabled style={{ opacity: 0.8 }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>DEPARTMENT</label>
                <input type="text" className="input-field" value={profileData.department} disabled style={{ opacity: 0.8 }} />
              </div>
            </div>

            <button type="submit" className="btn-primary">
              <Save size={16} />
              <span>Save Profile Changes</span>
            </button>
          </form>
        </div>
      )}

      {/* Tab 2: Security */}
      {activeTab === 'security' && (
        <div className="glass-card" style={{ padding: '28px', maxWidth: '650px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px' }}>Security & Authentication</h3>
          <form onSubmit={handleSave}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>CURRENT PASSWORD</label>
              <input
                type="password"
                className="input-field"
                placeholder="••••••••••••"
                value={securityData.currentPassword}
                onChange={(e) => setSecurityData(s => ({ ...s, currentPassword: e.target.value }))}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>NEW PASSWORD</label>
                <input
                  type="password"
                  className="input-field"
                  placeholder="••••••••••••"
                  value={securityData.newPassword}
                  onChange={(e) => setSecurityData(s => ({ ...s, newPassword: e.target.value }))}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>CONFIRM PASSWORD</label>
                <input
                  type="password"
                  className="input-field"
                  placeholder="••••••••••••"
                  value={securityData.confirmPassword}
                  onChange={(e) => setSecurityData(s => ({ ...s, confirmPassword: e.target.value }))}
                />
              </div>
            </div>

            <div style={{ marginBottom: '20px', padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={securityData.mfaEnabled}
                  onChange={(e) => setSecurityData(s => ({ ...s, mfaEnabled: e.target.checked }))}
                  style={{ accentColor: 'var(--accent-cyan)', width: '16px', height: '16px' }}
                />
                <span>Enable Multi-Factor Authentication (MFA)</span>
              </label>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', marginLeft: '26px' }}>
                Requires TOTP hardware key or authenticator app token upon login.
              </p>
            </div>

            <button type="submit" className="btn-primary">
              <Save size={16} />
              <span>Update Password & Security</span>
            </button>
          </form>
        </div>
      )}

      {/* Tab 3: Notifications */}
      {activeTab === 'notifications' && (
        <div className="glass-card" style={{ padding: '28px', maxWidth: '650px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px' }}>Alert Notifications & Routing</h3>
          <form onSubmit={handleSave}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={notificationData.emailAlerts}
                  onChange={(e) => setNotificationData(n => ({ ...n, emailAlerts: e.target.checked }))}
                  style={{ accentColor: 'var(--accent-cyan)', width: '16px', height: '16px' }}
                />
                <span>Email Security Alert Dispatch</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={notificationData.criticalOnly}
                  onChange={(e) => setNotificationData(n => ({ ...n, criticalOnly: e.target.checked }))}
                  style={{ accentColor: 'var(--accent-cyan)', width: '16px', height: '16px' }}
                />
                <span>Filter: Dispatch Only Critical & High Severity Alerts</span>
              </label>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>SLACK / TEAMS WEBHOOK URL</label>
                <input
                  type="text"
                  className="input-field"
                  value={notificationData.slackWebhook}
                  onChange={(e) => setNotificationData(n => ({ ...n, slackWebhook: e.target.value }))}
                />
              </div>
            </div>

            <button type="submit" className="btn-primary">
              <Save size={16} />
              <span>Save Notification Rules</span>
            </button>
          </form>
        </div>
      )}

      {/* Tab 4: Appearance */}
      {activeTab === 'appearance' && (
        <div className="glass-card" style={{ padding: '28px', maxWidth: '650px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px' }}>Console Appearance & Theme</h3>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {theme === 'dark' ? <Moon size={24} color="var(--accent-purple)" /> : <Sun size={24} color="var(--accent-amber)" />}
              <div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Current Theme: {theme === 'dark' ? 'Dark Security Mode' : 'Light Enterprise Mode'}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Toggle console color palette across all views
                </div>
              </div>
            </div>

            <button onClick={toggleTheme} className="btn-primary">
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              <span>Switch to {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Tab 5: ML & System Spec */}
      {activeTab === 'ml_specs' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* ML Model Specs */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={20} color="var(--accent-cyan)" />
              <span>Machine Learning Model Architecture</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Classifier Algorithm</span>
                <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>Gradient Boosting Classifier</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Input Behavioral Features</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>19 Features</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Model Artifact Path</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>ml/models/gb.pkl</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Scaler Artifact Path</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>ml/models/scaler.pkl</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Feature Order Artifact</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>ml/models/feature_columns.pkl</span>
              </div>
            </div>
          </div>

          {/* Dataset & Security Policy Specs */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={20} color="var(--accent-purple)" />
              <span>Dataset & Security Constraints</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Source Dataset</span>
                <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>CERT Insider Threat Dataset r4.2</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Total Dataset Size</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>330,452 User-Day Records</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Working Hours Boundary</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-amber)' }}>08:00 - 18:00</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>ML Notebook Pipeline State</span>
                <span className="badge badge-low">READ-ONLY / UNTOUCHED</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
