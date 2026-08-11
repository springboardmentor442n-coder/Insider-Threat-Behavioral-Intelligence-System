import { Users, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import GlassCard from "../ui/GlassCard";

export default function TopSuspiciousEmployees({
  employees = [],
}) {
  const navigate = useNavigate();

  // Dashboard intentionally shows only the same
  // five employees as the Investigation Queue.
  const visibleEmployees = employees.slice(0, 5);

  return (
    <GlassCard className="min-w-0 p-5 sm:p-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="mb-5 flex items-center justify-between gap-3">

        <div className="flex min-w-0 items-center gap-3">

          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10">
            <Users className="h-5 w-5 text-cyan-400" />
          </div>

          <div className="min-w-0">
            <h2 className="truncate text-lg font-bold text-white sm:text-xl">
              Top Suspicious Employees
            </h2>

            <p className="mt-0.5 text-xs text-slate-500">
              Highest behavioral risk scores
            </p>
          </div>

        </div>

        <span className="shrink-0 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-400">
          {visibleEmployees.length} Results
        </span>

      </div>

      {/* ======================================================
          TABLE
      ====================================================== */}

      <div className="min-w-0">

        {/* Table header */}

        <div className="grid grid-cols-[minmax(0,1.7fr)_minmax(70px,0.8fr)_auto] gap-3 border-b border-slate-800 px-2 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500 sm:grid-cols-[minmax(0,1.8fr)_minmax(90px,1fr)_70px_70px]">

          <span>Employee</span>
          <span className="hidden sm:block">Department</span>
          <span className="text-right">Risk</span>
          <span className="hidden text-right sm:block">Level</span>

        </div>

        {/* Rows */}

        <div>

          {visibleEmployees.length > 0 ? (
            visibleEmployees.map((emp, index) => {
              const risk = Number(emp.risk_score || 0);

              const severity =
                emp.severity ||
                emp.risk_level ||
                (risk >= 80
                  ? "Critical"
                  : risk >= 60
                  ? "High"
                  : risk >= 40
                  ? "Medium"
                  : "Low");

              const severityClass =
                severity === "Critical"
                  ? "bg-red-500/10 text-red-400 border-red-500/20"
                  : severity === "High"
                  ? "bg-orange-500/10 text-orange-400 border-orange-500/20"
                  : severity === "Medium"
                  ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";

              return (
                <div
                  key={emp.user || index}
                  className="
                    grid
                    grid-cols-[minmax(0,1.7fr)_minmax(70px,0.8fr)_auto]
                    items-center
                    gap-3
                    border-b
                    border-slate-800/70
                    px-2
                    py-3
                    transition
                    hover:bg-cyan-500/5
                    sm:grid-cols-[minmax(0,1.8fr)_minmax(90px,1fr)_70px_70px]
                  "
                >

                  {/* Employee */}

                  <div className="min-w-0">

                    <p className="truncate text-sm font-semibold text-slate-200">
                      {emp.employee_name || emp.user || "Unknown Employee"}
                    </p>

                    <p className="truncate text-[11px] text-slate-500">
                      {emp.user || "CERT Employee"}
                    </p>

                  </div>

                  {/* Department */}

                  <span className="hidden truncate text-xs text-slate-400 sm:block">
                    {emp.department || "CERT Dataset"}
                  </span>

                  {/* Risk */}

                  <span
                    className={`
                      text-right
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

                  {/* Severity */}

                  <span
                    className={`
                      hidden
                      rounded-full
                      border
                      px-2
                      py-1
                      text-center
                      text-[10px]
                      font-semibold
                      sm:block
                      ${severityClass}
                    `}
                  >
                    {severity}
                  </span>

                </div>
              );
            })
          ) : (
            <div className="px-4 py-8 text-center">
              <p className="text-sm text-slate-400">
                No suspicious employees found.
              </p>
            </div>
          )}

        </div>

      </div>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <button
        type="button"
        onClick={() => navigate("/employees")}
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
        View All Employees
        <ArrowRight className="h-3.5 w-3.5" />
      </button>

    </GlassCard>
  );
}
