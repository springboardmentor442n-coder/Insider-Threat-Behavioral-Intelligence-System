import { Routes, Route } from "react-router-dom";

import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";

// Feature Pages
import EmployeesPage from "../features/employees/pages/EmployeesPage";
import ThreatCenterPage from "../features/threats/pages/ThreatCenterPage";

// Layout & Auth
import AppShell from "../layouts/AppShell";
import ProtectedRoute from "../components/auth/ProtectedRoute";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Login */}
      <Route
        path="/login"
        element={<LoginPage />}
      />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        {/* Dashboard */}
        <Route
          index
          element={<DashboardPage />}
        />

        {/* Employees */}
        <Route
          path="employees"
          element={<EmployeesPage />}
        />

        {/* Threat Center */}
        <Route
          path="threats"
          element={<ThreatCenterPage />}
        />
      </Route>
    </Routes>
  );
}
