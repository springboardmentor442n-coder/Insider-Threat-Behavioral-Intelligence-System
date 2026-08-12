import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";

import {
  Search,
  RefreshCcw,
  ShieldAlert,
  FileText,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";

import useInvestigation from "../hooks/useInvestigation";
import useInvestigationDetail from "../hooks/useInvestigationDetail";

import EmployeeProfileCard from "../components/EmployeeProfileCard";
import InvestigationOverviewCards from "../components/InvestigationOverviewCards";
import InvestigationTimeline from "../components/InvestigationTimeline";

import { useAuth } from "../../../providers/AuthProvider";
import investigationService from "../api/investigationService";
import PageHeader from "../../../components/shared/PageHeader";

export default function InvestigationPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const caseIdParam = searchParams.get("caseId") || searchParams.get("employee");

  const {
    cases,
    loading,
    error,
    refetch,
  } = useInvestigation();

  const [search, setSearch] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState("");

  useEffect(() => {
    if (!cases.length) {
      setSelectedCaseId("");
      return;
    }

    if (caseIdParam) {
      const match = cases.find(
        (item) =>
          item.id?.toString().toLowerCase() === caseIdParam.toLowerCase() ||
          item.employee?.toString().toLowerCase() === caseIdParam.toLowerCase() ||
          item.user?.toString().toLowerCase() === caseIdParam.toLowerCase()
      );

      if (match) {
        setSelectedCaseId(match.id);
        return;
      }
    }

    const selectedStillExists = cases.some(
      (item) => item.id === selectedCaseId
    );

    if (!selectedStillExists) {
      setSelectedCaseId(cases[0].id);
    }
  }, [cases, selectedCaseId, caseIdParam]);

  /*
  |--------------------------------------------------------------------------
  | Selected investigation detail
  |--------------------------------------------------------------------------
  */

  const {
    caseData,
    loading: detailLoading,
    fetching: detailFetching,
    error: detailError,
    refetch: refetchDetail,
  } = useInvestigationDetail(selectedCaseId);

  /*
  |--------------------------------------------------------------------------
  | Search
  |--------------------------------------------------------------------------
  */

  const filteredCases = useMemo(() => {
    const query = search.toLowerCase().trim();

    if (!query) {
      return cases;
    }

    return cases.filter((item) => {
      return (
        item.id
          ?.toString()
          .toLowerCase()
          .includes(query) ||

        item.employee
          ?.toLowerCase()
          .includes(query) ||

        item.employee_name
          ?.toLowerCase()
          .includes(query) ||

        item.department
          ?.toLowerCase()
          .includes(query) ||

        item.prediction
          ?.toLowerCase()
          .includes(query) ||

        item.threat_type
          ?.toLowerCase()
          .includes(query) ||

        item.status
          ?.toLowerCase()
          .includes(query)
      );
    });
  }, [cases, search]);

  /*
  |--------------------------------------------------------------------------
  | Selected list item
  |--------------------------------------------------------------------------
  */

  const selectedListCase =
    cases.find(
      (item) => item.id === selectedCaseId
    ) ?? null;

  /*
  |--------------------------------------------------------------------------
  | Selected investigation
  |--------------------------------------------------------------------------
  |
  | Detail API is preferred.
  | List data remains visible while detail loads.
  |
  */

  const selectedCase =
    caseData ??
    selectedListCase;

  /*
  |--------------------------------------------------------------------------
  | Select case
  |--------------------------------------------------------------------------
  */

  const handleSelectCase = (caseId) => {
    setSelectedCaseId(caseId);
  };

  /*
  |--------------------------------------------------------------------------
  | Refresh
  |--------------------------------------------------------------------------
  */

  const handleRefresh = async () => {
    try {
      await refetch();

      if (selectedCaseId) {
        await refetchDetail();
      }

      toast.success(
        "Investigation data refreshed."
      );
    } catch {
      toast.error(
        "Unable to refresh investigation data."
      );
    }
  };

  const handleAssignToMe = async () => {
    if (!selectedCaseId) return;
    try {
      await investigationService.assignCase(selectedCaseId, user?.username || "Analyst");
      toast.success("Case assigned successfully.");
      refetchDetail();
      refetch();
    } catch {
      toast.error("Failed to assign case.");
    }
  };

  const handleEscalate = async () => {
    if (!selectedCaseId) return;
    try {
      await investigationService.escalateCase(selectedCaseId);
      toast.success("Case escalated to higher severity.");
      refetchDetail();
      refetch();
    } catch {
      toast.error("Failed to escalate case.");
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (!selectedCaseId) return;
    try {
      await investigationService.updateStatus(selectedCaseId, newStatus);
      toast.success(`Case status updated to ${newStatus}.`);
      refetchDetail();
      refetch();
    } catch {
      toast.error("Failed to update status.");
    }
  };

  /*
  |--------------------------------------------------------------------------
  | Loading
  |--------------------------------------------------------------------------
  */

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="flex items-center gap-3 text-cyan-400">
          <Loader2
            size={22}
            className="animate-spin"
          />

          Loading investigations...
        </div>
      </div>
    );
  }

  /*
  |--------------------------------------------------------------------------
  | Error
  |--------------------------------------------------------------------------
  */

  if (error) {
    return (
      <div
        className="
          rounded-2xl
          border border-red-500/30
          bg-red-500/10
          p-6
        "
      >
        <h2 className="text-xl font-semibold text-red-400">
          Failed to load investigations
        </h2>

        <p className="mt-2 text-slate-400">
          {error?.message ||
            "Unable to retrieve investigation data."}
        </p>

        <button
          type="button"
          onClick={handleRefresh}
          className="
            mt-4
            flex
            items-center
            gap-2
            rounded-xl
            border
            border-cyan-500/30
            bg-cyan-500/10
            px-4
            py-2
            text-cyan-300
            transition
            hover:bg-cyan-500/20
          "
        >
          <RefreshCcw size={18} />

          Try Again
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6"
    >
      {/* =====================================================
          HEADER
      ====================================================== */}

      {/* =====================================================
          HEADER
      ====================================================== */}

      <PageHeader
        icon={ShieldAlert}
        title="Investigation Center"
        subtitle="Active insider-threat investigations, case management, and analyst response"
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-[11px] font-semibold text-cyan-300">
            <FileText size={13} />
            {cases.length} {cases.length === 1 ? "Case" : "Cases"}
          </span>
        }
      />

      {/* =====================================================
          SEARCH + REFRESH
      ====================================================== */}

      <section
        className="
          flex
          flex-wrap
          items-center
          justify-between
          gap-4
          rounded-2xl
          border
          border-cyan-500/20
          bg-slate-900/70
          p-4
        "
      >
        <div className="relative">
          <Search
            size={18}
            className="
              absolute
              left-3
              top-1/2
              -translate-y-1/2
              text-slate-400
            "
          />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search cases, employees..."
            className="
              w-80
              rounded-xl
              border
              border-slate-700
              bg-slate-800
              py-2
              pl-10
              pr-4
              text-white
              outline-none
              transition
              focus:border-cyan-400
            "
          />
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={detailFetching}
          className="
            flex
            items-center
            gap-2
            rounded-xl
            border
            border-cyan-500/30
            bg-cyan-500/10
            px-4
            py-2
            text-cyan-300
            transition
            hover:bg-cyan-500/20
            disabled:cursor-not-allowed
            disabled:opacity-60
          "
        >
          <RefreshCcw
            size={18}
            className={
              detailFetching
                ? "animate-spin"
                : ""
            }
          />

          Refresh
        </button>
      </section>

      {/* =====================================================
          INVESTIGATION CASES
      ====================================================== */}

      <section
        className="
          rounded-2xl
          border
          border-slate-700
          bg-slate-900/60
          p-6
        "
      >
        <div className="mb-5 flex items-center gap-3">
          <FileText
            size={22}
            className="text-cyan-400"
          />

          <h2 className="text-xl font-semibold text-white">
            Investigation Cases
          </h2>

          <span
            className="
              rounded-full
              bg-cyan-500/10
              px-3
              py-1
              text-sm
              text-cyan-300
            "
          >
            {filteredCases.length}
          </span>
        </div>

        {filteredCases.length === 0 ? (
          <div
            className="
              rounded-xl
              border
              border-slate-700
              bg-slate-800/40
              p-5
            "
          >
            <p className="text-slate-400">
              No investigation cases found.
            </p>
          </div>
        ) : (
          <div className="grid gap-3">
            {filteredCases.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() =>
                  handleSelectCase(item.id)
                }
                className={`
                  w-full
                  rounded-xl
                  border
                  p-4
                  text-left
                  transition
                  ${
                    selectedCaseId === item.id
                      ? "border-cyan-400/50 bg-cyan-500/10"
                      : "border-slate-700 bg-slate-800/40 hover:border-cyan-500/30"
                  }
                `}
              >
                <div
                  className="
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-4
                  "
                >
                  <div>
                    <p className="font-semibold text-white">
                      {item.id}
                    </p>

                    <p className="mt-1 text-slate-400">
                      {item.employee}
                      {" • "}
                      {item.department}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="text-red-400">
                      Risk: {item.risk_score}
                    </span>

                    <span
                      className={`
                        rounded-full
                        px-3
                        py-1
                        text-xs
                        font-semibold
                        ${
                          item.status === "Resolved"
                            ? "bg-green-500/10 text-green-400"
                            : item.status === "Investigating"
                              ? "bg-yellow-500/10 text-yellow-400"
                              : "bg-red-500/10 text-red-400"
                        }
                      `}
                    >
                      {item.status}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* =====================================================
          SELECTED INVESTIGATION
      ====================================================== */}

      {selectedCase && (
        <>
          {detailError && (
            <div
              className="
                rounded-xl
                border
                border-red-500/30
                bg-red-500/10
                p-4
              "
            >
              <p className="text-red-400">
                Unable to load detailed investigation
                data for {selectedCaseId}.
              </p>
            </div>
          )}

          {detailLoading && (
            <div
              className="
                flex
                items-center
                gap-3
                rounded-xl
                border
                border-cyan-500/20
                bg-slate-900/60
                p-4
                text-cyan-400
              "
            >
              <Loader2
                size={20}
                className="animate-spin"
              />

              Loading case details...
            </div>
          )}

          {/* Action Bar */}
          <section className="mb-4 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-4 backdrop-blur-xl">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">Incident Response Actions:</span>
              <button
                type="button"
                onClick={handleAssignToMe}
                className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-3.5 py-1.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-500/20"
              >
                Assign To Me ({user?.username || "Analyst"})
              </button>
              <button
                type="button"
                onClick={handleEscalate}
                className="rounded-xl border border-red-500/30 bg-red-500/10 px-3.5 py-1.5 text-xs font-semibold text-red-300 transition hover:bg-red-500/20"
              >
                Escalate Severity
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">Case Status:</span>
              <select
                value={selectedCase.status || "Open"}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 focus:border-cyan-500 focus:outline-none"
              >
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Escalated">Escalated</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
          </section>

          <InvestigationOverviewCards
            employee={selectedCase}
          />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1">
              <EmployeeProfileCard
                employee={selectedCase}
              />
            </div>

            <div className="lg:col-span-2">
              <InvestigationTimeline
                employee={selectedCase}
                timeline={selectedCase.evidence || []}
            />
            </div>
          </div>

          {/* =================================================
              NOTES
          ================================================== */}

          <section
            className="
              rounded-2xl
              border
              border-slate-700
              bg-slate-900/60
              p-6
            "
          >
            <h2 className="text-xl font-semibold text-white">
              Investigation Notes
            </h2>

            <div
              className="
                mt-4
                rounded-xl
                border
                border-slate-700
                bg-slate-800/50
                p-5
              "
            >
              <p className="text-slate-300">
                {selectedCase.notes ||
                  "No investigation notes available."}
              </p>
            </div>
          </section>
        </>
      )}
    </motion.div>
  );
}
