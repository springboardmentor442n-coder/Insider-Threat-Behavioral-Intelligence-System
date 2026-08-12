import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Clock,
  HardDrive,
  Monitor,
  Globe,
  Mail,
  Activity,
  Search,
  CheckCircle2,
  XCircle,
  Info,
  X,
  UserCheck,
  ChevronRight,
  TrendingUp,
  FileSpreadsheet,
  Users,
} from "lucide-react";
import verificationService from "../../services/api/verificationService";
import investigationService from "../../features/investigation/api/investigationService";
import PageHeader from "../../components/shared/PageHeader";

const VECTOR_ICONS = {
  temporal: Clock,
  device: HardDrive,
  multi_pc: Monitor,
  web: Globe,
  email: Mail,
  overall_volume: Activity
};

export default function VerificationPage() {
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRiskFilter, setSelectedRiskFilter] = useState("ALL");
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [employeeDetail, setEmployeeDetail] = useState(null);
  const navigate = useNavigate();
  const [creatingCase, setCreatingCase] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleCreateInvestigation = async (userId) => {
    if (!userId) return;
    try {
      setCreatingCase(true);
      await investigationService.createCase(userId);
      navigate("/investigation");
    } catch (err) {
      console.error("Failed to create investigation case:", err);
    } finally {
      setCreatingCase(false);
    }
  };

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await verificationService.getBehavioralSummary();
      setSummaryData(data);
    } catch (err) {
      console.error("Failed to load behavioral validation summary:", err);
      setError(err.response?.data?.detail || "Failed to load verification data from server.");
    } finally {
      setLoading(false);
    }
  };

  const handleInspectEmployee = async (userId) => {
    setSelectedEmployee(userId);
    setDetailLoading(true);
    try {
      const detail = await verificationService.getEmployeeBehavioralEvidence(userId);
      setEmployeeDetail(detail);
    } catch (err) {
      console.error("Error fetching employee behavioral evidence:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedEmployee(null);
    setEmployeeDetail(null);
  };

  // Filter employees
  const filteredEmployees = (summaryData?.validated_employees || []).filter((emp) => {
    const matchesSearch = emp.user.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = selectedRiskFilter === "ALL" || emp.risk_level.toUpperCase() === selectedRiskFilter.toUpperCase();
    return matchesSearch && matchesRisk;
  });

  if (loading) {
    return (
      <div className="flex h-[70vh] w-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
          <p className="text-sm font-medium text-slate-400">Loading CERT Behavioral Pattern Validation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-red-400">
          <h3 className="flex items-center gap-2 text-lg font-semibold">
            <AlertTriangle className="h-5 w-5" /> Error Loading Verification Data
          </h3>
          <p className="mt-2 text-sm text-slate-300">{error}</p>
          <button
            onClick={fetchSummary}
            className="mt-4 rounded-lg bg-red-500/20 px-4 py-2 text-sm font-medium text-red-300 hover:bg-red-500/30"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5 pb-6 text-slate-100">
      {/* =====================================================
          HEADER
          ===================================================== */}
      <PageHeader
        icon={ShieldCheck}
        title="CERT Behavioral Pattern Validation"
        subtitle="Layer 2 Behavioral Consistency Validation Against CERT R4.2 Anomaly Dimensions"
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-400">
            <UserCheck className="h-3.5 w-3.5" /> Unsupervised ML Verified
          </span>
        }
      />

      {/* =====================================================
          METHODOLOGY DISCLAIMER BANNER
          ===================================================== */}
      <div className="relative overflow-hidden rounded-xl border border-cyan-500/20 bg-gradient-to-r from-cyan-950/40 via-slate-900/60 to-slate-950/80 p-4 backdrop-blur-md">
        <div className="flex items-start gap-3">
          <Info className="mt-0.5 h-5 w-5 shrink-0 text-cyan-400" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
              Methodological Distinction
            </h4>
            <p className="text-xs leading-relaxed text-slate-300">
              {summaryData?.disclaimer ||
                "Behavioral Pattern Validation is an independent behavioral consistency check against CERT-documented anomaly dimensions. It is not ground-truth classification because official CERT malicious-user labels are not currently available."}
            </p>
          </div>
        </div>
      </div>

      {/* =====================================================
          SUMMARY METRICS CARDS
          ===================================================== */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Evaluated */}
        <div className="rounded-xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Population</span>
            <Users className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">
              {summaryData?.total_employees?.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400">Employees</span>
          </div>
          <p className="mt-1 text-xs text-slate-500">Full CERT R4.2 enterprise pool</p>
        </div>

        {/* ML Suspicious */}
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-xs font-semibold uppercase tracking-wider">ML Flagged Suspicious</span>
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-amber-300">
              {summaryData?.suspicious_employees_count}
            </span>
            <span className="text-xs font-medium text-amber-400">
              {((summaryData?.suspicious_employees_count / summaryData?.total_employees) * 100).toFixed(1)}%
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">Consensus ≥ 3 or High/Critical Risk</p>
        </div>

        {/* Behavioral Validated */}
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Behaviorally Validated</span>
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-300">
              {summaryData?.validated_employees_count}
            </span>
            <span className="text-xs font-medium text-emerald-400">
              {((summaryData?.validated_employees_count / summaryData?.suspicious_employees_count) * 100).toFixed(1)}% Behavioral Validation Rate
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            {summaryData?.validated_employees_count} of {summaryData?.suspicious_employees_count} ML-flagged employees show support from ≥ 2 CERT behavioral vectors
          </p>
        </div>

        {/* Vectors Tested */}
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-cyan-400">
            <span className="text-xs font-semibold uppercase tracking-wider">CERT Vectors Tested</span>
            <Activity className="h-5 w-5" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-cyan-300">6</span>
            <span className="text-xs font-medium text-cyan-400">P90 Thresholds</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">Logon, USB, PC, Web, Email, Volume</p>
        </div>
      </div>

      {/* =====================================================
          BEHAVIORAL VECTOR MATRIX
          ===================================================== */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold tracking-tight text-white">
          CERT Behavioral Anomaly Vector Matrix
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(summaryData?.vector_summaries || []).map((v) => {
            const Icon = VECTOR_ICONS[v.vector_id] || Activity;
            return (
              <div
                key={v.vector_id}
                className="group relative overflow-hidden rounded-xl border border-white/10 bg-slate-900/60 p-5 transition-all hover:border-cyan-500/40 hover:bg-slate-900/80"
              >
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-white/5 p-2 text-cyan-400 group-hover:bg-cyan-500/10">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="rounded-full bg-cyan-500/10 px-2.5 py-0.5 text-xs font-bold text-cyan-400 ring-1 ring-cyan-500/20">
                    {v.anomalous_count} Users ({v.percentage}%)
                  </span>
                </div>
                <h3 className="mt-3 text-base font-semibold text-white">{v.vector_name}</h3>
                <p className="mt-0.5 text-xs font-medium text-cyan-400">{v.cert_dimension}</p>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">{v.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* =====================================================
          SUSPICIOUS EMPLOYEE BEHAVIORAL EVIDENCE TABLE
          ===================================================== */}
      <div className="space-y-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-white">
              Suspicious Employee Behavioral Evidence
            </h2>
            <p className="text-xs text-slate-400">
              Evaluates whether ML-detected suspicious users exhibit statistically anomalous CERT behavioral vectors.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search user ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-44 rounded-lg border border-white/10 bg-slate-900/80 py-1.5 pl-9 pr-3 text-xs text-white placeholder-slate-400 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            {/* Filter */}
            <select
              value={selectedRiskFilter}
              onChange={(e) => setSelectedRiskFilter(e.target.value)}
              className="rounded-lg border border-white/10 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-300 focus:border-cyan-500 focus:outline-none"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-900/60 backdrop-blur-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-white/10 bg-slate-950/60 uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">User ID</th>
                  <th className="px-4 py-3 font-semibold">Risk Score</th>
                  <th className="px-4 py-3 font-semibold">Risk Level</th>
                  <th className="px-4 py-3 font-semibold">Models Triggered</th>
                  <th className="px-4 py-3 font-semibold">Consensus %</th>
                  <th className="px-4 py-3 font-semibold">Vectors Flagged</th>
                  <th className="px-4 py-3 font-semibold">CERT Evidence Status</th>
                  <th className="px-4 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredEmployees.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-500">
                      No matching employees found.
                    </td>
                  </tr>
                ) : (
                  filteredEmployees.map((emp) => (
                    <tr
                      key={emp.user}
                      className="transition-colors hover:bg-white/[0.02]"
                    >
                      <td className="px-4 py-3 font-mono font-bold text-white">
                        {emp.user}
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-200">
                        {emp.risk_score}
                      </td>
                      <td className="px-4 py-3">
                        <RiskBadge level={emp.risk_level} />
                      </td>
                      <td className="px-4 py-3 font-medium text-slate-300">
                        {emp.suspicious_model_count} / 7
                      </td>
                      <td className="px-4 py-3 font-medium text-slate-300">
                        {emp.consensus_percentage}%
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {emp.vectors_flagged_names.map((name) => (
                            <span
                              key={name}
                              className="rounded bg-white/5 px-2 py-0.5 text-[10px] font-medium text-cyan-300 ring-1 ring-white/10"
                            >
                              {name}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {emp.supported_by_behavioral_evidence ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Validated ({emp.vectors_flagged_count} Vectors)
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-slate-400">
                            <Info className="h-3.5 w-3.5" /> Partial ({emp.vectors_flagged_count} Vector)
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleInspectEmployee(emp.user)}
                          className="inline-flex items-center gap-1 rounded-md bg-cyan-500/10 px-2.5 py-1 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/20 ring-1 ring-cyan-500/30"
                        >
                          Inspect Evidence <ChevronRight className="h-3 w-3" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* =====================================================
          INDIVIDUAL EMPLOYEE EVIDENCE MODAL / DRAWER
          ===================================================== */}
      <AnimatePresence>
        {selectedEmployee && (
          <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="h-full w-full max-w-2xl overflow-y-auto border-l border-white/10 bg-slate-950 p-6 shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Employee Behavioral Evidence: {selectedEmployee}
                  </h3>
                  <p className="text-xs text-slate-400">
                    CERT R4.2 Population Baseline Comparison & Vector Evaluation
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCreateInvestigation(selectedEmployee)}
                    disabled={creatingCase}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-cyan-500/20 px-3 py-1.5 text-xs font-bold text-cyan-300 hover:bg-cyan-500/30 border border-cyan-500/40 transition-colors"
                  >
                    <ShieldAlert className="h-4 w-4 text-cyan-400" />
                    {creatingCase ? "Opening..." : "Create Investigation"}
                  </button>
                  <button
                    onClick={closeModal}
                    className="rounded-lg p-2 text-slate-400 hover:bg-white/10 hover:text-white"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {detailLoading || !employeeDetail ? (
                <div className="flex h-64 items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
                </div>
              ) : (
                <div className="mt-6 space-y-6">
                  {/* Overview Card */}
                  <div className="rounded-xl border border-white/10 bg-slate-900/60 p-4">
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                      <div>
                        <span className="text-[10px] font-semibold uppercase text-slate-400">Risk Score</span>
                        <p className="text-xl font-bold text-white">{employeeDetail.risk_score}</p>
                      </div>
                      <div>
                        <span className="text-[10px] font-semibold uppercase text-slate-400">Risk Level</span>
                        <div className="mt-0.5">
                          <RiskBadge level={employeeDetail.risk_level} />
                        </div>
                      </div>
                      <div>
                        <span className="text-[10px] font-semibold uppercase text-slate-400">Models Triggered</span>
                        <p className="text-xl font-bold text-cyan-400">{employeeDetail.suspicious_model_count} / 7</p>
                      </div>
                      <div>
                        <span className="text-[10px] font-semibold uppercase text-slate-400">Consensus %</span>
                        <p className="text-xl font-bold text-emerald-400">{employeeDetail.consensus_percentage}%</p>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 ring-1 ring-emerald-500/20">
                      <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                      <p className="text-xs text-emerald-300">
                        {employeeDetail.supported_by_behavioral_evidence
                          ? "This employee's ML threat status is supported by multiple statistically anomalous CERT behavioral vectors."
                          : "This employee exhibits partial behavioral vector anomalies."}
                      </p>
                    </div>
                  </div>

                  {/* Vectors List */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                      Behavioral Vector Baseline Comparisons
                    </h4>

                    {(employeeDetail.behavioral_vectors || []).map((v) => {
                      const Icon = VECTOR_ICONS[v.vector_id] || Activity;
                      return (
                        <div
                          key={v.vector_id}
                          className={`rounded-xl border p-4 transition-all ${
                            v.anomalous
                              ? "border-amber-500/30 bg-amber-500/5"
                              : "border-white/10 bg-slate-900/40"
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2.5">
                              <div className={`rounded-lg p-2 ${v.anomalous ? "bg-amber-500/10 text-amber-400" : "bg-white/5 text-slate-400"}`}>
                                <Icon className="h-5 w-5" />
                              </div>
                              <div>
                                <h5 className="text-sm font-bold text-white">{v.vector_name}</h5>
                                <p className="text-xs text-slate-400">{v.cert_dimension}</p>
                              </div>
                            </div>
                            <span
                              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                                v.anomalous
                                  ? "bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/30"
                                  : "bg-slate-800 text-slate-400"
                              }`}
                            >
                              {v.anomalous ? "ANOMALOUS" : "NORMAL"}
                            </span>
                          </div>

                          {/* Stats Grid */}
                          <div className="mt-3 grid grid-cols-2 gap-2 rounded-lg bg-slate-950/40 p-3 text-xs sm:grid-cols-4">
                            <div>
                              <span className="text-[10px] text-slate-400">Employee Value</span>
                              <p className="font-bold text-white">{v.employee_value.toLocaleString()}</p>
                            </div>
                            <div>
                              <span className="text-[10px] text-slate-400">Pop. Median</span>
                              <p className="font-medium text-slate-300">{v.population_median.toLocaleString()}</p>
                            </div>
                            <div>
                              <span className="text-[10px] text-slate-400">Pop. P90 Threshold</span>
                              <p className="font-medium text-slate-300">{v.population_p90.toLocaleString()}</p>
                            </div>
                            <div>
                              <span className="text-[10px] text-slate-400">Percentile Rank</span>
                              <p className="font-bold text-cyan-400">{v.percentile}th</p>
                            </div>
                          </div>

                          {/* Evidence Text */}
                          <p className="mt-2 text-xs leading-relaxed text-slate-300">
                            {v.evidence}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function UsersIcon(props) {
  return (
    <svg
      {...props}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function RiskBadge({ level }) {
  const styles = {
    CRITICAL: "bg-red-500/20 text-red-300 border-red-500/30",
    HIGH: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    MEDIUM: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    LOW: "bg-slate-500/20 text-slate-300 border-slate-500/30"
  };

  const current = styles[level?.toUpperCase()] || styles.LOW;

  return (
    <span className={`inline-block rounded border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${current}`}>
      {level}
    </span>
  );
}
