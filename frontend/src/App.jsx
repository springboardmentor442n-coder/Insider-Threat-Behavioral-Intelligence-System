import React, { useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ThreatCenter from './pages/ThreatCenter';
import Users from './pages/Users';
import UserDetails from './pages/UserDetails';
import Analytics from './pages/Analytics';
import ThreatDetection from './pages/ThreatDetection';
import Models from './pages/Models';
import Explainability from './pages/Explainability';
import Alerts from './pages/Alerts';
import Investigations from './pages/Investigations';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) {
    return <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '100px' }}>Authenticating Session...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="threat-center" element={<ThreatCenter />} />
        <Route path="employees" element={<Users />} />
        <Route path="users" element={<Users />} />
        <Route path="user-details" element={<UserDetails />} />
        <Route path="users/:userId" element={<UserDetails />} />
        <Route path="upload-analyze" element={<ThreatDetection />} />
        <Route path="threat-detection" element={<ThreatDetection />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="models" element={<Models />} />
        <Route path="explainability" element={<Explainability />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="investigations" element={<Investigations />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
