import GlassCard from "../ui/GlassCard";
import { useTopSuspicious } from "../../hooks/queries/useTopSuspicious";

export default function AIInsightsPanel() {
  const { data, isLoading } = useTopSuspicious();

  if (isLoading) {
    return (
      <GlassCard className="p-6 h-[420px] flex items-center justify-center">
        Loading AI Insights...
      </GlassCard>
    );
  }

  const employee = data?.[0];

  return (
    <GlassCard className="p-6 h-[420px]">
      <h2 className="text-xl font-semibold mb-6">
        AI Recommendation
      </h2>

      {employee ? (
        <>
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 mb-5">
            <h3 className="font-semibold text-red-400">
              Highest Risk Employee
            </h3>

            <p className="mt-2">
              {employee.employee_name}
            </p>

            <p className="text-sm text-slate-400">
              Risk Score: {employee.risk_score}
            </p>
          </div>

          <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-4">
            <h3 className="font-semibold text-cyan-400">
              AI Recommendation
            </h3>

            <p className="mt-2 text-sm text-slate-300">
              Launch an investigation, review recent login activity,
              USB activity, email communication and web browsing.
            </p>
          </div>
        </>
      ) : (
        <p>No suspicious employees found.</p>
      )}
    </GlassCard>
  );
}
