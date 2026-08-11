import { useMemo, useState } from "react";

import {
  Search,
  Users,
  ShieldAlert,
  AlertTriangle,
  Activity,
  ShieldCheck,
  Download,
  ChevronDown,
  RefreshCw,
  Eye,
  X,
  Brain,
  CheckCircle2,
  CircleAlert,
} from "lucide-react";

import {
  useEmployees,
  useEmployeeIntelligenceSummary,
  useEmployeeIntelligence,
} from "../../hooks/queries/useEmployees";

// ============================================================
// HELPERS
// ============================================================

function normalizeRiskScore(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return 0;
  }

  if (number >= 0 && number <= 1) {
    return Number((number * 100).toFixed(2));
  }

  return Number(
    Math.min(
      100,
      Math.max(0, number)
    ).toFixed(2)
  );
}

// ============================================================
// RISK LEVEL
// ============================================================

function getRiskLevel(score) {
  const value = normalizeRiskScore(score);

  if (value >= 80) {
    return "Critical";
  }

  if (value >= 60) {
    return "High";
  }

  if (value >= 30) {
    return "Medium";
  }

  return "Low";
}

// ============================================================
// RISK STYLES
// ============================================================

function riskClasses(level) {
  switch (level) {
    case "Critical":
      return {
        badge:
          "border-red-500/30 bg-red-500/10 text-red-400",

        dot:
          "bg-red-500",

        text:
          "text-red-400",
      };

    case "High":
      return {
        badge:
          "border-orange-500/30 bg-orange-500/10 text-orange-400",

        dot:
          "bg-orange-500",

        text:
          "text-orange-400",
      };

    case "Medium":
      return {
        badge:
          "border-yellow-500/30 bg-yellow-500/10 text-yellow-400",

        dot:
          "bg-yellow-500",

        text:
          "text-yellow-400",
      };

    default:
      return {
        badge:
          "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",

        dot:
          "bg-emerald-500",

        text:
          "text-emerald-400",
      };
  }
}

// ============================================================
// EMPLOYEE INITIALS
// ============================================================

function initials(user) {
  if (!user) {
    return "??";
  }

  return String(user)
    .slice(0, 2)
    .toUpperCase();
}

// ============================================================
// MODEL NAME
// ============================================================

function formatModelName(name) {
  return name
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (char) => char.toUpperCase()
    );
}

// ============================================================
// EMPLOYEE DETAILS DRAWER
// ============================================================

function EmployeeDetails({
  user,
  onClose,
}) {
  const {
    data,
    isLoading,
    isError,
  } = useEmployeeIntelligence(user);

  if (!user) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">

      {/* ======================================================
          BACKDROP
      ====================================================== */}

      <button
        type="button"
        aria-label="Close employee details"
        onClick={onClose}
        className="
          absolute
          inset-0
          bg-black/60
          backdrop-blur-sm
        "
      />

      {/* ======================================================
          DRAWER
      ====================================================== */}

      <div
        className="
          relative
          z-10
          h-full
          w-full
          max-w-2xl
          overflow-y-auto
          border-l
          border-slate-800
          bg-slate-950
          shadow-2xl
        "
      >

        {/* ====================================================
            HEADER
        ==================================================== */}

        <div
          className="
            sticky
            top-0
            z-20
            flex
            items-center
            justify-between
            border-b
            border-slate-800
            bg-slate-950/95
            px-6
            py-5
            backdrop-blur
          "
        >

          <div>

            <p
              className="
                text-xs
                font-medium
                uppercase
                tracking-wider
                text-cyan-400
              "
            >
              CERT Employee Intelligence
            </p>

            <h2
              className="
                mt-1
                text-2xl
                font-bold
                text-white
              "
            >
              {user}
            </h2>

          </div>

          <button
            type="button"
            onClick={onClose}
            className="
              rounded-xl
              border
              border-slate-700
              p-2
              text-slate-400
              transition
              hover:bg-slate-800
              hover:text-white
            "
          >
            <X className="h-5 w-5" />
          </button>

        </div>

        {/* ====================================================
            LOADING
        ==================================================== */}

        {isLoading && (
          <div
            className="
              flex
              min-h-[400px]
              items-center
              justify-center
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
                text-slate-400
              "
            >
              <RefreshCw
                className="
                  h-5
                  w-5
                  animate-spin
                  text-cyan-400
                "
              />

              Loading employee intelligence...
            </div>
          </div>
        )}

        {/* ====================================================
            ERROR
        ==================================================== */}

        {isError && (
          <div
            className="
              m-6
              rounded-xl
              border
              border-red-500/20
              bg-red-500/10
              p-5
              text-red-400
            "
          >
            Unable to load employee intelligence.
          </div>
        )}

        {/* ====================================================
            DATA
        ==================================================== */}

        {data &&
          !isLoading &&
          !isError && (
            <div className="space-y-6 p-6">

              {/* ==================================================
                  RISK OVERVIEW
              ================================================== */}

              <div
                className="
                  grid
                  grid-cols-2
                  gap-4
                "
              >

                {/* Risk Score */}

                <div
                  className="
                    rounded-2xl
                    border
                    border-slate-800
                    bg-slate-900/70
                    p-5
                  "
                >

                  <p className="text-sm text-slate-400">
                    Risk Score
                  </p>

                  <p
                    className={`
                      mt-2
                      text-4xl
                      font-bold
                      ${
                        riskClasses(
                          data.risk_level
                        ).text
                      }
                    `}
                  >
                    {normalizeRiskScore(
                      data.risk_score
                    )}
                  </p>

                  <p
                    className="
                      mt-1
                      text-xs
                      text-slate-500
                    "
                  >
                    Out of 100
                  </p>

                </div>

                {/* Risk Level */}

                <div
                  className="
                    rounded-2xl
                    border
                    border-slate-800
                    bg-slate-900/70
                    p-5
                  "
                >

                  <p className="text-sm text-slate-400">
                    Risk Level
                  </p>

                  <div
                    className={`
                      mt-3
                      inline-flex
                      items-center
                      gap-2
                      rounded-full
                      border
                      px-3
                      py-1.5
                      text-sm
                      font-semibold
                      ${
                        riskClasses(
                          data.risk_level
                        ).badge
                      }
                    `}
                  >

                    <span
                      className={`
                        h-2
                        w-2
                        rounded-full
                        ${
                          riskClasses(
                            data.risk_level
                          ).dot
                        }
                      `}
                    />

                    {data.risk_level}
                  </div>

                </div>

                {/* Rank */}

                <div
                  className="
                    rounded-2xl
                    border
                    border-slate-800
                    bg-slate-900/70
                    p-5
                  "
                >

                  <p className="text-sm text-slate-400">
                    Rank
                  </p>

                  <p
                    className="
                      mt-2
                      text-3xl
                      font-bold
                      text-white
                    "
                  >
                    #{data.rank}
                  </p>

                </div>

                {/* Consensus */}

                <div
                  className="
                    rounded-2xl
                    border
                    border-slate-800
                    bg-slate-900/70
                    p-5
                  "
                >

                  <p className="text-sm text-slate-400">
                    Model Consensus
                  </p>

                  <p
                    className="
                      mt-2
                      text-3xl
                      font-bold
                      text-cyan-400
                    "
                  >
                    {data.consensus_percentage}%
                  </p>

                  <p
                    className="
                      mt-1
                      text-xs
                      text-slate-500
                    "
                  >
                    {data.suspicious_count} / 7
                    models suspicious
                  </p>

                </div>

              </div>

              {/* ==================================================
                  PREDICTION
              ================================================== */}

              <div
                className="
                  rounded-2xl
                  border
                  border-slate-800
                  bg-slate-900/70
                  p-5
                "
              >

                <div
                  className="
                    flex
                    items-center
                    gap-3
                  "
                >

                  <div
                    className="
                      rounded-xl
                      bg-cyan-500/10
                      p-2
                    "
                  >
                    <Brain
                      className="
                        h-5
                        w-5
                        text-cyan-400
                      "
                    />
                  </div>

                  <div>

                    <p
                      className="
                        text-xs
                        uppercase
                        tracking-wider
                        text-slate-500
                      "
                    >
                      Behavioral Prediction
                    </p>

                    <p
                      className="
                        mt-1
                        text-lg
                        font-semibold
                        text-white
                      "
                    >
                      {data.prediction ||
                        (data.suspicious_count > 0
                          ? "Suspicious"
                          : "Normal")}
                    </p>

                  </div>

                </div>

              </div>

              {/* ==================================================
                  ML MODEL RESULTS
              ================================================== */}

              <div>

                <div
                  className="
                    mb-3
                    flex
                    items-center
                    gap-2
                  "
                >

                  <Activity
                    className="
                      h-5
                      w-5
                      text-cyan-400
                    "
                  />

                  <h3
                    className="
                      text-lg
                      font-semibold
                      text-white
                    "
                  >
                    ML Model Results
                  </h3>

                </div>

                <div className="space-y-2">

                  {[
                    "isolation_forest",
                    "one_class_svm",
                    "lof",
                    "elliptic_envelope",
                    "pca",
                    "dbscan",
                    "kmeans",
                  ].map((model) => {

                    const predictionKey =
                      `${model}_prediction`;

                    const scoreKey =
                      `${model}_score`;

                    const prediction =
                      data[predictionKey];

                    const suspicious =
                      prediction ===
                      "Suspicious";

                    return (
                      <div
                        key={model}
                        className="
                          flex
                          items-center
                          justify-between
                          rounded-xl
                          border
                          border-slate-800
                          bg-slate-900/50
                          px-4
                          py-3
                        "
                      >

                        <div
                          className="
                            flex
                            items-center
                            gap-3
                          "
                        >

                          {suspicious ? (
                            <CircleAlert
                              className="
                                h-4
                                w-4
                                text-red-400
                              "
                            />
                          ) : (
                            <CheckCircle2
                              className="
                                h-4
                                w-4
                                text-emerald-400
                              "
                            />
                          )}

                          <span
                            className="
                              text-sm
                              text-slate-300
                            "
                          >
                            {formatModelName(model)}
                          </span>

                        </div>

                        <div
                          className="
                            flex
                            items-center
                            gap-4
                          "
                        >

                          <span
                            className={
                              suspicious
                                ? "text-sm font-semibold text-red-400"
                                : "text-sm font-semibold text-emerald-400"
                            }
                          >
                            {prediction}
                          </span>

                          <span
                            className="
                              min-w-24
                              text-right
                              text-xs
                              text-slate-500
                            "
                          >
                            {Number(
                              data[scoreKey] ?? 0
                            ).toFixed(4)}
                          </span>

                        </div>

                      </div>
                    );
                  })}

                </div>

              </div>

              {/* ==================================================
                  WEIGHTED SCORE
              ================================================== */}

              <div
                className="
                  rounded-2xl
                  border
                  border-cyan-500/20
                  bg-cyan-500/5
                  p-5
                "
              >

                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >

                  <div>

                    <p
                      className="
                        text-sm
                        text-slate-400
                      "
                    >
                      Weighted Risk Score
                    </p>

                    <p
                      className="
                        mt-1
                        text-xs
                        text-slate-500
                      "
                    >
                      Combined score from all
                      anomaly detection models
                    </p>

                  </div>

                  <p
                    className="
                      text-2xl
                      font-bold
                      text-cyan-400
                    "
                  >
                    {normalizeRiskScore(
                      data.weighted_score
                    )}
                  </p>

                </div>

              </div>

            </div>
          )}

      </div>
    </div>
  );
}

// ============================================================
// MAIN PAGE
// ============================================================

export default function EmployeesPage() {

  const {
    data: employees = [],
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useEmployees();

  const {
    data: summary,
  } = useEmployeeIntelligenceSummary();

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    riskFilter,
    setRiskFilter,
  ] = useState("All");

  const [
    sortOrder,
    setSortOrder,
  ] = useState("risk-desc");

  const [
    selectedUser,
    setSelectedUser,
  ] = useState(null);

  // ==========================================================
  // NORMALIZE DATA
  // ==========================================================

  const normalizedEmployees =
    useMemo(() => {

      return employees.map(
        (employee) => {

          const riskScore =
            normalizeRiskScore(
              employee.risk_score
            );

          const riskLevel =
            employee.risk_level ||
            getRiskLevel(riskScore);

          return {
            ...employee,

            risk_score:
              riskScore,

            risk_level:
              riskLevel,
          };
        }
      );

    }, [employees]);

  // ==========================================================
  // FILTER + SEARCH + SORT
  // ==========================================================

  const filteredEmployees =
    useMemo(() => {

      let result = [
        ...normalizedEmployees,
      ];

      const searchValue =
        search
          .trim()
          .toLowerCase();

      // Search employee ID
      if (searchValue) {

        result =
          result.filter(
            (employee) =>
              String(
                employee.user ?? ""
              )
                .toLowerCase()
                .includes(
                  searchValue
                )
          );
      }

      // Risk filter
      if (
        riskFilter !== "All"
      ) {

        result =
          result.filter(
            (employee) =>
              employee.risk_level ===
              riskFilter
          );
      }

      // Highest risk
      if (
        sortOrder === "risk-desc"
      ) {

        result.sort(
          (a, b) =>
            b.risk_score -
            a.risk_score
        );
      }

      // Lowest risk
      if (
        sortOrder === "risk-asc"
      ) {

        result.sort(
          (a, b) =>
            a.risk_score -
            b.risk_score
        );
      }

      // Model rank
      if (
        sortOrder === "rank"
      ) {

        result.sort(
          (a, b) =>
            Number(
              a.rank ?? 999999
            ) -
            Number(
              b.rank ?? 999999
            )
        );
      }

      return result;

    }, [
      normalizedEmployees,
      search,
      riskFilter,
      sortOrder,
    ]);

  // ==========================================================
  // SUMMARY
  // ==========================================================

  const totalEmployees =
    summary?.totalEmployees ??
    normalizedEmployees.length;

  const averageRisk =
    summary?.averageRisk ?? 0;

  const highestRisk =
    summary?.highestRisk ?? 0;

  const lowestRisk =
    summary?.lowestRisk ?? 0;

  const criticalCount =
    normalizedEmployees.filter(
      (employee) =>
        employee.risk_level ===
        "Critical"
    ).length;

  const highCount =
    normalizedEmployees.filter(
      (employee) =>
        employee.risk_level ===
        "High"
    ).length;

  const mediumCount =
    normalizedEmployees.filter(
      (employee) =>
        employee.risk_level ===
        "Medium"
    ).length;

  const lowCount =
    normalizedEmployees.filter(
      (employee) =>
        employee.risk_level ===
        "Low"
    ).length;

  // ==========================================================
  // EXPORT
  // ==========================================================

  function exportEmployees() {

    if (
      !filteredEmployees.length
    ) {
      return;
    }

    const headers = [
      "Rank",
      "User",
      "Risk Score",
      "Risk Level",
      "Suspicious Count",
      "Consensus Percentage",
      "Prediction",
    ];

    const rows =
      filteredEmployees.map(
        (employee) => [
          employee.rank ?? "",
          employee.user ?? "",
          employee.risk_score ?? "",
          employee.risk_level ?? "",
          employee.suspicious_count ?? "",
          employee.consensus_percentage ?? "",
          employee.prediction ?? "",
        ]
      );

    const csv = [
      headers,
      ...rows,
    ]
      .map(
        (row) =>
          row
            .map(
              (value) =>
                `"${String(
                  value
                ).replaceAll(
                  '"',
                  '""'
                )}"`
            )
            .join(",")
      )
      .join("\n");

    const blob =
      new Blob(
        [csv],
        {
          type:
            "text/csv;charset=utf-8;",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const link =
      document.createElement(
        "a"
      );

    link.href = url;

    link.download =
      "employee-intelligence.csv";

    document.body.appendChild(
      link
    );

    link.click();

    link.remove();

    URL.revokeObjectURL(
      url
    );
  }

  // ==========================================================
  // LOADING
  // ==========================================================

  if (isLoading) {

    return (
      <div
        className="
          flex
          min-h-[500px]
          items-center
          justify-center
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
            text-slate-400
          "
        >

          <RefreshCw
            className="
              h-5
              w-5
              animate-spin
              text-cyan-400
            "
          />

          Loading live employee
          intelligence...

        </div>

      </div>
    );
  }

  // ==========================================================
  // ERROR
  // ==========================================================

  if (isError) {

    return (
      <div className="space-y-6">

        <div>

          <p
            className="
              text-sm
              font-medium
              uppercase
              tracking-wider
              text-cyan-400
            "
          >
            CERT Behavioral Intelligence
          </p>

          <h1
            className="
              mt-2
              text-3xl
              font-bold
              text-white
            "
          >
            Employees
          </h1>

        </div>

        <div
          className="
            rounded-2xl
            border
            border-red-500/20
            bg-red-500/10
            p-6
          "
        >

          <div
            className="
              flex
              items-start
              gap-4
            "
          >

            <CircleAlert
              className="
                mt-0.5
                h-6
                w-6
                text-red-400
              "
            />

            <div>

              <h2
                className="
                  font-semibold
                  text-red-300
                "
              >
                Unable to load employee
                intelligence
              </h2>

              <p
                className="
                  mt-1
                  text-sm
                  text-red-400/80
                "
              >
                The frontend could not
                retrieve the CERT ML
                employee dataset.
              </p>

              <button
                type="button"
                onClick={() =>
                  refetch()
                }
                className="
                  mt-4
                  rounded-lg
                  bg-red-500/10
                  px-4
                  py-2
                  text-sm
                  font-medium
                  text-red-300
                  hover:bg-red-500/20
                "
              >
                Retry
              </button>

            </div>

          </div>

        </div>

      </div>
    );
  }

  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <div className="space-y-6">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div
        className="
          flex
          flex-col
          justify-between
          gap-4
          xl:flex-row
          xl:items-center
        "
      >

        <div>

          <div
            className="
              flex
              items-center
              gap-3
            "
          >

            <div
              className="
                rounded-xl
                bg-cyan-500/10
                p-2.5
              "
            >
              <Users
                className="
                  h-6
                  w-6
                  text-cyan-400
                "
              />
            </div>

            <div>

              <h1
                className="
                  text-3xl
                  font-bold
                  tracking-tight
                  text-white
                "
              >
                Employees
              </h1>

              <p
                className="
                  mt-1
                  text-sm
                  text-slate-400
                "
              >
                Live CERT insider-threat
                behavioral intelligence
              </p>

            </div>

          </div>

        </div>

        <div
          className="
            flex
            items-center
            gap-3
          "
        >

          {/* LIVE INDICATOR */}

          <div
            className="
              flex
              items-center
              gap-2
              rounded-full
              border
              border-emerald-500/20
              bg-emerald-500/5
              px-3
              py-2
              text-xs
              font-medium
              text-emerald-400
            "
          >

            <span
              className="
                h-2
                w-2
                animate-pulse
                rounded-full
                bg-emerald-400
              "
            />

            Live Data

          </div>

          {/* REFRESH */}

          <button
            type="button"
            onClick={() =>
              refetch()
            }
            disabled={isFetching}
            className="
              flex
              items-center
              gap-2
              rounded-xl
              border
              border-slate-700
              bg-slate-900
              px-4
              py-2.5
              text-sm
              font-medium
              text-slate-300
              transition
              hover:border-slate-600
              hover:bg-slate-800
              hover:text-white
              disabled:opacity-50
            "
          >

            <RefreshCw
              className={`h-4 w-4 ${
                isFetching
                  ? "animate-spin"
                  : ""
              }`}
            />

            Refresh

          </button>

        </div>

      </div>

      {/* ======================================================
          SUMMARY CARDS
      ====================================================== */}

      <div
        className="
          grid
          grid-cols-1
          gap-4
          sm:grid-cols-2
          xl:grid-cols-5
        "
      >

        <SummaryCard
          title="Employees"
          value={totalEmployees}
          icon={Users}
          iconClass="
            bg-cyan-500/10
            text-cyan-400
          "
        />

        <SummaryCard
          title="Critical"
          value={criticalCount}
          icon={ShieldAlert}
          iconClass="
            bg-red-500/10
            text-red-400
          "
        />

        <SummaryCard
          title="High"
          value={highCount}
          icon={AlertTriangle}
          iconClass="
            bg-orange-500/10
            text-orange-400
          "
        />

        <SummaryCard
          title="Medium"
          value={mediumCount}
          icon={Activity}
          iconClass="
            bg-yellow-500/10
            text-yellow-400
          "
        />

        <SummaryCard
          title="Low"
          value={lowCount}
          icon={ShieldCheck}
          iconClass="
            bg-emerald-500/10
            text-emerald-400
          "
        />

      </div>

      {/* ======================================================
          DATA STATISTICS
      ====================================================== */}

      <div
        className="
          grid
          grid-cols-1
          gap-4
          md:grid-cols-3
        "
      >

        <StatCard
          label="Average Risk"
          value={`${Number(
            averageRisk
          ).toFixed(2)}%`}
        />

        <StatCard
          label="Highest Risk"
          value={`${Number(
            highestRisk
          ).toFixed(2)}%`}
        />

        <StatCard
          label="Lowest Risk"
          value={`${Number(
            lowestRisk
          ).toFixed(2)}%`}
        />

      </div>

      {/* ======================================================
          TOOLBAR
      ====================================================== */}

      <div
        className="
          rounded-2xl
          border
          border-slate-800
          bg-slate-900/60
          p-4
        "
      >

        <div
          className="
            flex
            flex-col
            gap-3
            xl:flex-row
          "
        >

          {/* SEARCH */}

          <div
            className="
              relative
              flex-1
            "
          >

            <Search
              className="
                absolute
                left-4
                top-1/2
                h-5
                w-5
                -translate-y-1/2
                text-slate-500
              "
            />

            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search employee ID..."
              className="
                h-12
                w-full
                rounded-xl
                border
                border-slate-700
                bg-slate-950
                pl-12
                pr-4
                text-sm
                text-white
                outline-none
                placeholder:text-slate-500
                focus:border-cyan-500/50
                focus:ring-2
                focus:ring-cyan-500/10
              "
            />

          </div>

          {/* RISK FILTER */}

          <div className="relative">

            <select
              value={riskFilter}
              onChange={(event) =>
                setRiskFilter(
                  event.target.value
                )
              }
              className="
                h-12
                min-w-44
                appearance-none
                rounded-xl
                border
                border-slate-700
                bg-slate-950
                px-4
                pr-10
                text-sm
                text-slate-300
                outline-none
                focus:border-cyan-500/50
              "
            >

              <option value="All">
                All Risk Levels
              </option>

              <option value="Critical">
                Critical
              </option>

              <option value="High">
                High
              </option>

              <option value="Medium">
                Medium
              </option>

              <option value="Low">
                Low
              </option>

            </select>

            <ChevronDown
              className="
                pointer-events-none
                absolute
                right-3
                top-1/2
                h-4
                w-4
                -translate-y-1/2
                text-slate-500
              "
            />

          </div>

          {/* SORT */}

          <div className="relative">

            <select
              value={sortOrder}
              onChange={(event) =>
                setSortOrder(
                  event.target.value
                )
              }
              className="
                h-12
                min-w-48
                appearance-none
                rounded-xl
                border
                border-slate-700
                bg-slate-950
                px-4
                pr-10
                text-sm
                text-slate-300
                outline-none
                focus:border-cyan-500/50
              "
            >

              <option value="risk-desc">
                Highest Risk
              </option>

              <option value="risk-asc">
                Lowest Risk
              </option>

              <option value="rank">
                Model Rank
              </option>

            </select>

            <ChevronDown
              className="
                pointer-events-none
                absolute
                right-3
                top-1/2
                h-4
                w-4
                -translate-y-1/2
                text-slate-500
              "
            />

          </div>

          {/* EXPORT */}

          <button
            type="button"
            onClick={
              exportEmployees
            }
            className="
              flex
              h-12
              items-center
              justify-center
              gap-2
              rounded-xl
              border
              border-slate-700
              bg-slate-800
              px-5
              text-sm
              font-medium
              text-slate-200
              transition
              hover:bg-slate-700
            "
          >

            <Download
              className="h-4 w-4"
            />

            Export

          </button>

        </div>

      </div>

      {/* ======================================================
          RESULT COUNT
      ====================================================== */}

      <div
        className="
          flex
          items-center
          justify-between
        "
      >

        <p
          className="
            text-sm
            text-slate-400
          "
        >
          Showing{" "}

          <span
            className="
              font-semibold
              text-white
            "
          >
            {filteredEmployees.length}
          </span>{" "}

          of{" "}

          <span
            className="
              font-semibold
              text-white
            "
          >
            {normalizedEmployees.length}
          </span>{" "}

          employees
        </p>

        <p
          className="
            text-xs
            text-slate-500
          "
        >
          Automatically refreshes every
          30 seconds
        </p>

      </div>

      {/* ======================================================
          TABLE
      ====================================================== */}

      <div
        className="
          overflow-hidden
          rounded-2xl
          border
          border-slate-800
          bg-slate-900/60
        "
      >

        <div className="overflow-x-auto">

          <table
            className="
              w-full
              min-w-[1000px]
            "
          >

            <thead>

              <tr
                className="
                  border-b
                  border-slate-800
                  bg-slate-900
                "
              >

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Rank
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Employee
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Risk Score
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Risk Level
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Suspicious Models
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-left
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Consensus
                </th>

                <th
                  className="
                    px-5
                    py-4
                    text-right
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Action
                </th>

              </tr>

            </thead>

            <tbody>

              {filteredEmployees.map(
                (employee) => {

                  const level =
                    employee.risk_level;

                  const styles =
                    riskClasses(level);

                  return (
                    <tr
                      key={
                        employee.user
                      }
                      className="
                        border-b
                        border-slate-800/70
                        transition
                        hover:bg-slate-800/30
                      "
                    >

                      {/* RANK */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <span
                          className="
                            font-mono
                            text-sm
                            font-semibold
                            text-slate-400
                          "
                        >
                          #{employee.rank}
                        </span>

                      </td>

                      {/* EMPLOYEE */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <div
                          className="
                            flex
                            items-center
                            gap-3
                          "
                        >

                          <div
                            className="
                              flex
                              h-10
                              w-10
                              items-center
                              justify-center
                              rounded-xl
                              bg-cyan-500/10
                              text-xs
                              font-bold
                              text-cyan-400
                            "
                          >
                            {initials(
                              employee.user
                            )}
                          </div>

                          <div>

                            <p
                              className="
                                font-semibold
                                text-white
                              "
                            >
                              {employee.user}
                            </p>

                            <p
                              className="
                                text-xs
                                text-slate-500
                              "
                            >
                              CERT Employee
                            </p>

                          </div>

                        </div>

                      </td>

                      {/* RISK SCORE */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <div
                          className="
                            min-w-32
                          "
                        >

                          <div
                            className="
                              mb-1
                              flex
                              items-center
                              justify-between
                            "
                          >

                            <span
                              className={`
                                font-semibold
                                ${styles.text}
                              `}
                            >
                              {employee.risk_score}
                            </span>

                            <span
                              className="
                                text-xs
                                text-slate-600
                              "
                            >
                              /100
                            </span>

                          </div>

                          <div
                            className="
                              h-1.5
                              overflow-hidden
                              rounded-full
                              bg-slate-800
                            "
                          >

                            <div
                              className={`
                                h-full
                                rounded-full
                                ${
                                  level ===
                                  "Critical"
                                    ? "bg-red-500"
                                    : level ===
                                      "High"
                                    ? "bg-orange-500"
                                    : level ===
                                      "Medium"
                                    ? "bg-yellow-500"
                                    : "bg-emerald-500"
                                }
                              `}
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    employee.risk_score
                                  )
                                )}%`,
                              }}
                            />

                          </div>

                        </div>

                      </td>

                      {/* RISK LEVEL */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <span
                          className={`
                            inline-flex
                            items-center
                            gap-2
                            rounded-full
                            border
                            px-3
                            py-1.5
                            text-xs
                            font-semibold
                            ${styles.badge}
                          `}
                        >

                          <span
                            className={`
                              h-1.5
                              w-1.5
                              rounded-full
                              ${styles.dot}
                            `}
                          />

                          {level}

                        </span>

                      </td>

                      {/* SUSPICIOUS MODELS */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <span
                          className="
                            font-semibold
                            text-white
                          "
                        >
                          {
                            employee.suspicious_count ??
                            0
                          }
                        </span>

                        <span
                          className="
                            text-slate-500
                          "
                        >
                          {" "}/ 7
                        </span>

                      </td>

                      {/* CONSENSUS */}

                      <td
                        className="
                          px-5
                          py-4
                        "
                      >

                        <span
                          className="
                            font-semibold
                            text-cyan-400
                          "
                        >
                          {
                            employee.consensus_percentage ??
                            0
                          }%
                        </span>

                      </td>

                      {/* ACTION */}

                      <td
                        className="
                          px-5
                          py-4
                          text-right
                        "
                      >

                        <button
                          type="button"
                          onClick={() =>
                            setSelectedUser(
                              employee.user
                            )
                          }
                          className="
                            inline-flex
                            items-center
                            gap-2
                            rounded-lg
                            border
                            border-slate-700
                            bg-slate-800/70
                            px-3
                            py-2
                            text-xs
                            font-medium
                            text-slate-300
                            transition
                            hover:border-cyan-500/30
                            hover:bg-cyan-500/10
                            hover:text-cyan-400
                          "
                        >

                          <Eye
                            className="
                              h-4
                              w-4
                            "
                          />

                          View

                        </button>

                      </td>

                    </tr>
                  );
                }
              )}

            </tbody>

          </table>

          {/* EMPTY STATE */}

          {filteredEmployees.length ===
            0 && (
            <div
              className="
                flex
                min-h-[300px]
                flex-col
                items-center
                justify-center
                px-6
                text-center
              "
            >

              <Users
                className="
                  h-12
                  w-12
                  text-slate-700
                "
              />

              <h3
                className="
                  mt-4
                  text-lg
                  font-semibold
                  text-white
                "
              >
                No matching employees
              </h3>

              <p
                className="
                  mt-1
                  text-sm
                  text-slate-500
                "
              >
                Try changing the search
                or risk filter.
              </p>

            </div>
          )}

        </div>

      </div>

      {/* ======================================================
          DETAILS DRAWER
      ====================================================== */}

      {selectedUser && (
        <EmployeeDetails
          user={selectedUser}
          onClose={() =>
            setSelectedUser(null)
          }
        />
      )}

    </div>
  );
}

// ============================================================
// SUMMARY CARD
// ============================================================

function SummaryCard({
  title,
  value,
  icon: Icon,
  iconClass,
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-800
        bg-slate-900/60
        p-5
        transition
        hover:border-slate-700
      "
    >

      <div
        className="
          flex
          items-start
          justify-between
        "
      >

        <div>

          <p
            className="
              text-xs
              font-medium
              uppercase
              tracking-wider
              text-slate-500
            "
          >
            {title}
          </p>

          <p
            className="
              mt-2
              text-3xl
              font-bold
              text-white
            "
          >
            {value}
          </p>

        </div>

        <div
          className={`
            rounded-xl
            p-3
            ${iconClass}
          `}
        >
          <Icon className="h-5 w-5" />
        </div>

      </div>

    </div>
  );
}

// ============================================================
// STAT CARD
// ============================================================

function StatCard({
  label,
  value,
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-800
        bg-slate-900/40
        px-5
        py-4
      "
    >

      <p
        className="
          text-xs
          uppercase
          tracking-wider
          text-slate-500
        "
      >
        {label}
      </p>

      <p
        className="
          mt-1
          text-xl
          font-semibold
          text-slate-200
        "
      >
        {value}
      </p>

    </div>
  );
}
