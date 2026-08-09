import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';

import LoginPage     from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import EmployeesPage from './pages/employees/EmployeesPage';
import EmployeeDetailPage from './pages/employees/EmployeeDetailPage';
import AnomaliesPage from './pages/anomalies/AnomaliesPage';
import RiskPage      from './pages/risk/RiskPage';
import AlertsPage    from './pages/alerts/AlertsPage';
import MLPage        from './pages/ml/MLPage';
import UEBAPage      from './pages/ueba/UEBAPage';
import PredictionPlaygroundPage from './pages/ml/PredictionPlaygroundPage';
import {
  IncidentsPage, ActivitiesPage, ReportsPage
} from './pages/incidents/IncidentsPage';

import './index.css';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div style={{
      minHeight:'100vh', background:'var(--bg-base)',
      display:'flex', alignItems:'center', justifyContent:'center',
      color:'var(--text-muted)', fontSize:'0.85rem',
    }}>Loading…</div>
  );
  return user ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{
          style: {
            background: 'var(--bg-card)', color: 'var(--text-primary)',
            border: '1px solid var(--border)', borderRadius: '8px', fontSize: '0.83rem',
          },
        }} />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"  element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/employees"  element={<ProtectedRoute><EmployeesPage /></ProtectedRoute>} />
          <Route path="/employees/:id" element={<ProtectedRoute><EmployeeDetailPage /></ProtectedRoute>} />
          <Route path="/activities" element={<ProtectedRoute><ActivitiesPage /></ProtectedRoute>} />
          <Route path="/anomalies"  element={<ProtectedRoute><AnomaliesPage /></ProtectedRoute>} />
          <Route path="/risk"       element={<ProtectedRoute><RiskPage /></ProtectedRoute>} />
          <Route path="/alerts"     element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
          <Route path="/incidents"  element={<ProtectedRoute><IncidentsPage /></ProtectedRoute>} />
          <Route path="/reports"    element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
          <Route path="/ml"         element={<ProtectedRoute><MLPage /></ProtectedRoute>} />
          <Route path="/ueba"        element={<ProtectedRoute><UEBAPage /></ProtectedRoute>} />
          <Route path="/predict"     element={<ProtectedRoute><PredictionPlaygroundPage /></ProtectedRoute>} />
          <Route path="/settings"   element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
