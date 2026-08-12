import { motion } from "framer-motion";
import {
    FileText,
    RefreshCcw,
    Download,
    Radio,
    X,
    Search,
    AlertCircle,
    FileSpreadsheet,
    FileCode,
} from "lucide-react";
import PageHeader from "../../../components/shared/PageHeader";
import { useMemo, useState } from "react";

import useReports from "../hooks/useReports";
import reportsService from "../api/reportsService";

import ReportsToolbar from "../components/ReportsToolbar";
import ReportsOverviewCards from "../components/ReportsOverviewCards";
import ReportsTable from "../components/ReportsTable";
import ReportsSkeleton from "../components/ReportsSkeleton";

function formatReportName(name) {
    if (!name) {
        return "Report";
    }

    return name
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) =>
            char.toUpperCase()
        );
}

import { formatPercent, formatScore, formatNumber, formatDecimal } from "../../../utils/formatters";

function formatCellValue(value, key = "") {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    const keyLower = String(key).toLowerCase();
    const isIdOrCode = keyLower.includes("id") || keyLower.includes("user") || keyLower === "rank";

    if (typeof value === "number" || (!isIdOrCode && !isNaN(value) && typeof value === "string" && value.trim() !== "")) {
        const num = Number(value);
        if (Number.isFinite(num)) {
            if (keyLower.includes("percent") || keyLower.includes("consensus")) {
                return formatPercent(num);
            }
            if (keyLower.includes("score")) {
                return formatScore(num);
            }
            return formatDecimal(num);
        }
    }

    return String(value);
}

function getPreviewColumns(records) {
    if (!records.length) {
        return [];
    }

    const preferredColumns = [
        "rank",
        "user",
        "employee_name",
        "risk_score",
        "risk_level",
        "severity",
        "status",
        "suspicious_count",
        "consensus_percentage",
        "weighted_score",
    ];

    const availableColumns = Object.keys(
        records[0]
    );

    const preferred = preferredColumns.filter(
        (column) =>
            availableColumns.includes(column)
    );

    if (preferred.length >= 5) {
        return preferred.slice(0, 8);
    }

    return availableColumns.slice(0, 8);
}

export default function ReportsPage() {
    const {
        reportList,
        reports,
        loading,
        refreshing,
        error,
        refetch,
    } = useReports();

    const [search, setSearch] = useState("");

    const [
        selectedReport,
        setSelectedReport,
    ] = useState(null);

    const [
        downloading,
        setDownloading,
    ] = useState(false);

    const filteredReports = useMemo(() => {
        const list = Array.isArray(reportList)
            ? reportList
            : [];

        if (!search.trim()) {
            return list;
        }

        const keyword =
            search.toLowerCase();

        return list.filter((report) => {
            return (
                report.name
                    ?.toLowerCase()
                    .includes(keyword) ||
                report.filename
                    ?.toLowerCase()
                    .includes(keyword)
            );
        });
    }, [reportList, search]);

    const selectedRecords =
        selectedReport &&
        Array.isArray(
            reports?.[selectedReport]
        )
            ? reports[selectedReport]
            : [];

    const previewRecords =
        selectedRecords.slice(0, 10);

    const previewColumns =
        getPreviewColumns(
            previewRecords
        );

    const selectedMetadata =
        reportList.find(
            (report) =>
                report.name ===
                selectedReport
        );

    const handleDownload = async (
        reportName,
        format = "csv"
    ) => {
        try {
            setDownloading(true);

            /*
             * The backend creates a fresh live report
             * at download time.
             */
            await reportsService.downloadReport(
                reportName,
                format
            );
        } catch (downloadError) {
            console.error(
                "Failed to download report:",
                downloadError
            );
        } finally {
            setDownloading(false);
        }
    };

    const handleRefresh = async () => {
        await refetch();
    };

    if (loading) {
        return <ReportsSkeleton />;
    }

    return (
        <motion.div
            initial={{
                opacity: 0,
                y: 8,
            }}
            animate={{
                opacity: 1,
                y: 0,
            }}
            transition={{
                duration: 0.25,
            }}
            className="space-y-5 pb-6"
        >
            {/* =====================================================
                HEADER
                ===================================================== */}

            {/* HEADER */}
            <PageHeader
                icon={FileText}
                title="Reports Center"
                subtitle="Current ML intelligence, investigation data and downloadable reports"
                badge={
                    <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
                        <Radio className="h-3 w-3 animate-pulse" />
                        Live
                    </span>
                }
            >
                <button
                    type="button"
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:border-slate-600 hover:bg-slate-800 hover:text-white disabled:opacity-50"
                >
                    <RefreshCcw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} />
                    Refresh
                </button>
            </PageHeader>

                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span>
                        Reports are refreshed from
                        the backend automatically.
                    </span>

                    <span className="hidden sm:inline">
                        •
                    </span>

                    <span>
                        Downloads are generated
                        at request time.
                    </span>
                </div>

            {/* =====================================================
                ERROR
                ===================================================== */}

            {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-400">
                    Failed to load reports.
                    Please refresh the page or
                    check the backend.
                </div>
            )}

            {/* =====================================================
                OVERVIEW
                ===================================================== */}

            <ReportsOverviewCards
                reportList={reportList}
            />

            {/* =====================================================
                TOOLBAR
                ===================================================== */}

            <ReportsToolbar
                search={search}
                setSearch={setSearch}
            />

            {/* =====================================================
                REPORT TABLE
                ===================================================== */}

            <ReportsTable
                reports={filteredReports}
                reportData={reports}
                selectedReport={
                    selectedReport
                }
                onSelectReport={
                    setSelectedReport
                }
                onDownload={
                    handleDownload
                }
            />

            {/* =====================================================
                PREVIEW
                ===================================================== */}

            {selectedReport && (
                <motion.section
                    initial={{
                        opacity: 0,
                        y: 8,
                    }}
                    animate={{
                        opacity: 1,
                        y: 0,
                    }}
                    className="
                        overflow-hidden
                        rounded-2xl
                        border
                        border-cyan-500/15
                        bg-slate-900/65
                    "
                >
                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-sm font-semibold text-white">
                                    {formatReportName(
                                        selectedReport
                                    )}
                                </h2>

                                {selectedMetadata?.live && (
                                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase text-emerald-400">
                                        <Radio className="h-3 w-3" />
                                        Live
                                    </span>
                                )}
                            </div>

                            <p className="mt-0.5 text-xs text-slate-500">
                                Showing{" "}
                                {Math.min(
                                    10,
                                    selectedRecords.length
                                )}{" "}
                                of{" "}
                                {selectedRecords.length.toLocaleString()}{" "}
                                records
                            </p>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() =>
                                    handleDownload(
                                        selectedReport
                                    )
                                }
                                disabled={
                                    downloading
                                }
                                className="
                                    inline-flex
                                    items-center
                                    gap-2
                                    rounded-lg
                                    bg-cyan-500/10
                                    px-3
                                    py-1.5
                                    text-xs
                                    font-medium
                                    text-cyan-300
                                    hover:bg-cyan-500/20
                                    disabled:opacity-50
                                "
                            >
                                <Download className="h-3.5 w-3.5" />

                                {downloading
                                    ? "Downloading..."
                                    : "Download"}
                            </button>

                            <button
                                type="button"
                                onClick={() =>
                                    setSelectedReport(
                                        null
                                    )
                                }
                                className="
                                    rounded-lg
                                    p-1.5
                                    text-slate-500
                                    transition
                                    hover:bg-white/5
                                    hover:text-slate-300
                                "
                                title="Close preview"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    </div>

                    {previewRecords.length === 0 ? (
                        <div className="px-4 py-10 text-center text-sm text-slate-500">
                            No records available.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[850px]">
                                <thead>
                                    <tr className="border-b border-white/10 text-left">
                                        {previewColumns.map(
                                            (column) => (
                                                <th
                                                    key={
                                                        column
                                                    }
                                                    className="
                                                        px-3
                                                        py-2.5
                                                        text-[10px]
                                                        font-semibold
                                                        uppercase
                                                        tracking-wide
                                                        text-slate-500
                                                    "
                                                >
                                                    {column.replaceAll(
                                                        "_",
                                                        " "
                                                    )}
                                                </th>
                                            )
                                        )}
                                    </tr>
                                </thead>

                                <tbody>
                                    {previewRecords.map(
                                        (
                                            record,
                                            index
                                        ) => (
                                            <tr
                                                key={
                                                    record.rank ??
                                                    record.user ??
                                                    record.id ??
                                                    index
                                                }
                                                className="border-b border-white/5 last:border-0"
                                            >
                                                {previewColumns.map(
                                                    (
                                                        column
                                                    ) => (
                                                        <td
                                                            key={
                                                                column
                                                            }
                                                            className="
                                                                max-w-[220px]
                                                                truncate
                                                                px-3
                                                                py-2.5
                                                                text-xs
                                                                text-slate-300
                                                            "
                                                        >
                                                            {formatCellValue(
                                                                record[
                                                                    column
                                                                ],
                                                                column
                                                            )}
                                                        </td>
                                                    )
                                                )}
                                            </tr>
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </motion.section>
            )}
        </motion.div>
    );
}
