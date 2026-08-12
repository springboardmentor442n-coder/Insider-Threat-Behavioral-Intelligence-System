import { Routes, Route, Navigate } from "react-router-dom";

// ============================================================
// PUBLIC PAGES
// ============================================================

import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";

// ============================================================
// APPLICATION PAGES
// ============================================================

import DashboardPage from "../pages/dashboard/DashboardPage";

// IMPORTANT:
// Use the ML-powered Employees page.
// The old feature-based EmployeesPage contains the CRUD
// employee interface and is not the ML intelligence page.
import EmployeesPage from "../pages/employees/EmployeesPage";

import ThreatCenterPage from "../features/threats/pages/ThreatCenterPage";
import AnalyticsPage from "../features/analytics/pages/AnalyticsPage";
import InvestigationPage from "../features/investigation/pages/InvestigationPage";
import ReportsPage from "../features/reports/pages/ReportsPage";

import ModelsPage from "../features/models/pages/ModelsPage";
import ExplainabilityPage from "../features/explainability/pages/ExplainabilityPage";

import SettingsPage from "../pages/settings/SettingsPage";
import AccountPage from "../pages/account/AccountPage";
import VerificationPage from "../pages/verification/VerificationPage";

// ============================================================
// LAYOUT / AUTH
// ============================================================

import AppShell from "../layouts/AppShell";
import ProtectedRoute from "../components/auth/ProtectedRoute";

// ============================================================
// ROUTES
// ============================================================

export default function AppRoutes() {
  return (
    <Routes>

      {/* ======================================================
          PUBLIC AUTHENTICATION
          ====================================================== */}

      {/* Login */}
      <Route
        path="/login"
        element={<LoginPage />}
      />

      {/* Registration */}
      <Route
        path="/register"
        element={<RegisterPage />}
      />


      {/* ======================================================
          ROOT
          ====================================================== */}

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<DashboardPage />}
        />
      </Route>


      {/* ======================================================
          DASHBOARD
          ====================================================== */}

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<DashboardPage />}
        />
      </Route>


      {/* ======================================================
          EMPLOYEES
          
          IMPORTANT:
          This now loads:
          
          src/pages/employees/EmployeesPage.jsx
          
          which is the ML-powered Employees page.
          ====================================================== */}

      <Route
        path="/employees"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<EmployeesPage />}
        />
      </Route>


      {/* ======================================================
          THREAT CENTER
          ====================================================== */}

      <Route
        path="/threats"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<ThreatCenterPage />}
        />
      </Route>


      {/* ======================================================
          ANALYTICS
          ====================================================== */}

      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<AnalyticsPage />}
        />
      </Route>


      {/* ======================================================
          MODELS
          ====================================================== */}

      <Route
        path="/models"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<ModelsPage />}
        />
      </Route>


      {/* ======================================================
          EXPLAINABILITY
          ====================================================== */}

      <Route
        path="/explainability"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<ExplainabilityPage />}
        />
      </Route>


      {/* ======================================================
          INVESTIGATION
          ====================================================== */}

      <Route
        path="/investigation"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<InvestigationPage />}
        />
      </Route>


      {/* ======================================================
          REPORTS
          ====================================================== */}

      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<ReportsPage />}
        />
      </Route>


      {/* ======================================================
          VERIFICATION (BEHAVIORAL PATTERN VALIDATION)
          ====================================================== */}

      <Route
        path="/verification"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<VerificationPage />}
        />
      </Route>


      {/* ======================================================
          ACCOUNT / PROFILE
          ====================================================== */}

      <Route
        path="/account"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<AccountPage />}
        />
      </Route>


      {/* ======================================================
          SETTINGS
          ====================================================== */}

      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<SettingsPage />}
        />
      </Route>


      {/* ======================================================
          UNKNOWN ROUTES
          ====================================================== */}

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />

    </Routes>
  );
}
