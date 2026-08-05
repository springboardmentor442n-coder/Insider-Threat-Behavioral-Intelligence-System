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

  if (isLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        Loading Dashboard...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-red-500 bg-red-500/10 p-6 text-red-400">
        Failed to load dashboard.
        <br />
        {error?.message}
      </div>
    );
  }

  return (
    <div className="space-y-8">

      <HeroBanner />

      <MetricGrid data={data} />

      <section className="grid gap-6 xl:grid-cols-3">

        <div className="xl:col-span-2">
          <ThreatTrendChart />
        </div>

        <AIInsightsPanel />

      </section>

      <section className="grid gap-6 xl:grid-cols-3">

        <div className="xl:col-span-2">
          <ActivityFeed />
        </div>

        <SystemStatus />

      </section>

      <section className="grid gap-6 xl:grid-cols-2">

        <InvestigationQueue
          employees={suspiciousEmployees}
        />

        <TopSuspiciousEmployees
          employees={suspiciousEmployees}
        />

      </section>

    </div>
  );
}
