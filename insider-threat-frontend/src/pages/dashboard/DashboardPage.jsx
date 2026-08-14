import HeroBanner from "../../components/dashboard/HeroBanner";
import MetricGrid from "../../components/dashboard/MetricGrid";
import ThreatTrendChart from "../../components/dashboard/ThreatTrendChart";
import ActivityFeed from "../../components/dashboard/ActivityFeed";
import AIInsightsPanel from "../../components/dashboard/AIInsightsPanel";
import InvestigationQueue from "../../components/dashboard/InvestigationQueue";
import SystemStatus from "../../components/dashboard/SystemStatus";
import TopSuspiciousEmployees from "../../components/dashboard/TopSuspiciousEmployees";

import {
  useDashboard,
  useTopSuspicious,
} from "../../hooks/queries/useDashboard";
import useAnalytics from "../../features/analytics/hooks/useAnalytics";
import useModels from "../../features/models/hooks/useModels";

import RiskDistributionChart from "../../features/analytics/charts/RiskDistributionChart";
import MonthlyTrendChart from "../../features/analytics/charts/MonthlyTrendChart";
import ModelsOverviewCards from "../../features/models/components/ModelsOverviewCards";

export default function DashboardPage() {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useDashboard();

  const {
    data: suspiciousEmployees = [],
    isLoading: suspiciousLoading,
  } = useTopSuspicious();

  const {
    riskDistribution,
    trainingTimes,
    loading: analyticsLoading,
  } = useAnalytics();

  const {
    summary: modelsSummary,
    loading: modelsLoading,
  } = useModels();

  // ============================================================
  // LOADING STATE
  // ============================================================

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />

          <div>
            <p className="text-lg font-semibold text-white">
              Loading Dashboard...
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Loading behavioral intelligence data
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // ERROR STATE
  // ============================================================

  if (isError) {
    return (
      <div className="px-1 sm:px-0">
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 shadow-lg">
          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-semibold text-red-400">
              Failed to load dashboard
            </h2>

            <p className="text-sm text-slate-400">
              The dashboard could not retrieve the latest behavioral
              intelligence data.
            </p>

            {error?.message && (
              <p className="mt-2 break-words rounded-lg bg-black/20 p-3 font-mono text-xs text-red-300">
                {error.message}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // DASHBOARD
  // ============================================================

  return (
    <main className="w-full min-w-0 space-y-8 pb-8">

      {/* ======================================================
          HERO
      ====================================================== */}

      <section className="w-full min-w-0">
        <HeroBanner />
      </section>

      {/* ======================================================
          SYSTEM OVERVIEW METRICS
      ====================================================== */}

      <section className="w-full min-w-0">
        <MetricGrid data={data} />
      </section>

      {/* ======================================================
          MODEL INTELLIGENCE OVERVIEW
      ====================================================== */}
      <section className="w-full min-w-0">
        <div className="mb-4">
          <h2 className="text-xl font-bold tracking-tight text-white">Model Intelligence</h2>
          <p className="text-sm text-slate-400">7-Model Unsupervised Ensemble Performance</p>
        </div>
        {!modelsLoading && <ModelsOverviewCards summary={modelsSummary} />}
      </section>

      {/* ======================================================
          THREAT ANALYTICS + AI INSIGHTS
      ====================================================== */}

      <section className="grid min-w-0 grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="min-w-0 xl:col-span-2 space-y-6">
          <ThreatTrendChart />
          {!analyticsLoading && (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <RiskDistributionChart data={riskDistribution} />
              <MonthlyTrendChart data={trainingTimes} />
            </div>
          )}
        </div>

        <div className="min-w-0">
          <AIInsightsPanel />
        </div>
      </section>

      {/* ======================================================
          ACTIVITY + SYSTEM STATUS
      ====================================================== */}

      <section className="grid min-w-0 grid-cols-1 gap-6 xl:grid-cols-3">

        <div className="min-w-0 xl:col-span-2">
          <ActivityFeed />
        </div>

        <div className="min-w-0">
          <SystemStatus />
        </div>

      </section>

      {/* ======================================================
          INVESTIGATION + TOP SUSPICIOUS EMPLOYEES
      ====================================================== */}

      <section className="grid min-w-0 grid-cols-1 gap-6 xl:grid-cols-2">

        <div className="min-w-0">
          <InvestigationQueue
            employees={
              suspiciousLoading
                ? []
                : suspiciousEmployees
            }
          />
        </div>

        <div className="min-w-0">
          <TopSuspiciousEmployees
            employees={
              suspiciousLoading
                ? []
                : suspiciousEmployees
            }
          />
        </div>

      </section>

    </main>
  );
}
