import { ShieldAlert, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import GlassCard from "../ui/GlassCard";

export default function InvestigationQueue({
  employees = [],
}) {
  const navigate = useNavigate();

  // Dashboard intentionally shows only a short preview.
  const visibleEmployees = employees.slice(0, 5);

  return (
    <GlassCard className="min-w-0 p-5 sm:p-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-500/10">
            <ShieldAlert className="h-5 w-5 text-red-400" />
          </div>

          <div className="min-w-0">
            <h2 className="truncate text-lg font-bold text-white sm:text-xl">
              Investigation Queue
            </h2>

            <p className="mt-0.5 text-xs text-slate-500">
              Highest-risk employees requiring attention
            </p>
          </div>
        </div>

        <span className="shrink-0 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-400">
          {visibleEmployees.length} Pending
        </span>
      </div>

      {/* ======================================================
          EMPLOYEE PREVIEW
      ====================================================== */}

      <div className="space-y-2.5">

        {visibleEmployees.length > 0 ? (
          visibleEmployees.map((emp, index) => {
            const risk = Number(emp.risk_score || 0);

            return (
              <div
                key={emp.user || index}
                className="
                  rounded-xl
                  border
                  border-slate-700/70
                  bg-slate-800/40
                  px-4
                  py-3
                  transition-all
                  duration-200
                  hover:border-cyan-500/30
                  hover:bg-cyan-500/5
                "
              >
                {/* Top row */}

                <div className="flex items-center justify-between gap-3">

                  <div className="min-w-0">
                    <h3 className="truncate text-sm font-semibold text-slate-100">
                      {emp.employee_name || emp.user || "Unknown Employee"}
                    </h3>

                    <p className="mt-0.5 truncate text-xs text-slate-500">
                      {emp.user || "CERT Employee"}
                      {emp.department
                        ? ` • ${emp.department}`
                        : ""}
                    </p>
                  </div>

                  <span
                    className={`
                      shrink-0
                      text-sm
                      font-bold
                      ${
                        risk >= 80
                          ? "text-red-400"
                          : risk >= 60
                          ? "text-orange-400"
                          : risk >= 40
                          ? "text-yellow-400"
                          : "text-emerald-400"
                      }
                    `}
                  >
                    {risk.toFixed(2)}
                  </span>

                </div>

                {/* Risk bar */}

                <div className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-slate-700/80">
                  <div
                    className={`
                      h-full
                      rounded-full
                      transition-all
                      duration-500
                      ${
                        risk >= 80
                          ? "bg-red-400"
                          : risk >= 60
                          ? "bg-orange-400"
                          : risk >= 40
                          ? "bg-yellow-400"
                          : "bg-emerald-400"
                      }
                    `}
                    style={{
                      width: `${Math.min(100, Math.max(0, risk))}%`,
                    }}
                  />
                </div>
              </div>
            );
          })
        ) : (
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-8 text-center">
            <p className="text-sm text-slate-400">
              No employees currently require investigation.
            </p>
          </div>
        )}

      </div>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <button
        type="button"
        onClick={() => navigate("/investigation")}
        className="
          mt-4
          flex
          w-full
          items-center
          justify-center
          gap-2
          rounded-lg
          border
          border-slate-700
          bg-slate-900/60
          px-4
          py-2
          text-xs
          font-medium
          text-slate-300
          transition
          hover:border-cyan-500/30
          hover:bg-cyan-500/10
          hover:text-cyan-300
        "
      >
        View Investigation Center
        <ArrowRight className="h-3.5 w-3.5" />
      </button>

    </GlassCard>
  );
}
