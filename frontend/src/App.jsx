import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, ROLES } from './context/AuthContext';
import Login from './pages/Login';
import AppShell from './components/AppShell';
import AnalystDashboard from './pages/dashboards/AnalystDashboard';
import SocDashboard from './pages/dashboards/SocDashboard';
import ManagerDashboard from './pages/dashboards/ManagerDashboard';
import AdminDashboard from './pages/dashboards/AdminDashboard';
import AlertQueue from './pages/AlertQueue';
import Investigations from './pages/Investigations';
import Employees from './pages/Employees';
import EntityAnalytics from './pages/EntityAnalytics';
import AuditLog from './pages/AuditLog';
import Reports from './pages/Reports';
import Loader from './components/Loader';

// Each role sees the dashboard built for their job. The backend enforces what
// each may actually fetch; this just routes them to the right home screen.
function RoleHome() {
  const { user } = useAuth();
  switch (user?.role) {
    case ROLES.SOC_ENGINEER:     return <SocDashboard />;
    case ROLES.SECURITY_MANAGER: return <ManagerDashboard />;
    case ROLES.ADMINISTRATOR:    return <AdminDashboard />;
    case ROLES.SECURITY_ANALYST:
    default:                     return <AnalystDashboard />;
  }
}

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Loader full label="Authenticating" />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

// Admin-only route guard - bounces non-admins back to their home.
function AdminOnly({ children }) {
  const { user } = useAuth();
  if (user?.role !== ROLES.ADMINISTRATOR) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          loading ? <Loader full label="Loading" />
          : user ? <Navigate to="/" replace />
          : <Login />
        }
      />
      <Route
        path="/"
        element={
          <Protected>
            <AppShell />
          </Protected>
        }
      >
        <Route index element={<RoleHome />} />
        <Route path="alerts" element={<AlertQueue />} />
        <Route path="investigations" element={<Investigations />} />
        <Route path="investigations/:userId" element={<Investigations />} />
        <Route path="employees" element={<Employees />} />
        <Route path="entity" element={<EntityAnalytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="entity/:userId" element={<EntityAnalytics />} />
        <Route path="audit" element={<AdminOnly><AuditLog /></AdminOnly>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
