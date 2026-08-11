import {
    Download,
    Eye,
    Radio,
    Database,
    FileWarning,
} from "lucide-react";

import reportsService from "../api/reportsService";

function getReportLabel(name) {
    if (!name) {
        return "Report";
    }

    return name
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) =>
            char.toUpperCase()
        );
}

export default function ReportsTable({
    reports,
    reportData,
    selectedReport,
    onSelectReport,
    onDownload,
}) {
    const rows = Array.isArray(reports)
        ? reports
        : [];

    return (
        <div className="overflow-hidden rounded-2xl border border-cyan-500/15 bg-slate-900/65">
            <div className="overflow-x-auto">
                <table className="w-full min-w-[760px]">
                    <thead>
                        <tr className="border-b border-white/10 bg-slate-950/30 text-left">
                            <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                Report
                            </th>

                            <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                Type
                            </th>

                            <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                Records
                            </th>

                            <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                Status
                            </th>

                            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                                Actions
                            </th>
                        </tr>
                    </thead>

                    <tbody>
                        {rows.length === 0 ? (
                            <tr>
                                <td
                                    colSpan={5}
                                    className="px-4 py-12 text-center"
                                >
                                    <FileWarning className="mx-auto h-7 w-7 text-slate-600" />

                                    <p className="mt-2 text-sm text-slate-400">
                                        No reports found.
                                    </p>
                                </td>
                            </tr>
                        ) : (
                            rows.map((report) => {
                                const data =
                                    reportData?.[
                                        report.name
                                    ];

                                const recordCount =
                                    Array.isArray(data)
                                        ? data.length
                                        : report.record_count ?? 0;

                                const isSelected =
                                    selectedReport ===
                                    report.name;

                                return (
                                    <tr
                                        key={report.name}
                                        className={`
                                            border-b
                                            border-white/5
                                            transition-colors
                                            ${
                                                isSelected
                                                    ? "bg-cyan-500/5"
                                                    : "hover:bg-white/[0.02]"
                                            }
                                        `}
                                    >
                                        <td className="px-4 py-3">
                                            <div className="min-w-0">
                                                <p className="truncate text-sm font-semibold text-white">
                                                    {getReportLabel(
                                                        report.name
                                                    )}
                                                </p>

                                                <p className="mt-0.5 max-w-[280px] truncate text-xs text-slate-500">
                                                    {report.filename}
                                                </p>
                                            </div>
                                        </td>

                                        <td className="px-4 py-3">
                                            {report.live ? (
                                                <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-400">
                                                    <Radio className="h-3 w-3" />
                                                    Live
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800/70 px-2.5 py-1 text-xs font-medium text-slate-400">
                                                    <Database className="h-3 w-3" />
                                                    Artifact
                                                </span>
                                            )}
                                        </td>

                                        <td className="px-4 py-3 text-sm text-slate-300">
                                            {recordCount.toLocaleString()}
                                        </td>

                                        <td className="px-4 py-3">
                                            {report.exists ? (
                                                <span className="text-xs font-medium text-emerald-400">
                                                    Available
                                                </span>
                                            ) : (
                                                <span className="text-xs font-medium text-red-400">
                                                    Missing
                                                </span>
                                            )}
                                        </td>

                                        <td className="px-4 py-3">
                                            <div className="flex justify-end gap-1.5">
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        onSelectReport(
                                                            report.name
                                                        )
                                                    }
                                                    className={`
                                                        rounded-lg
                                                        border
                                                        p-2
                                                        transition
                                                        ${
                                                            isSelected
                                                                ? "border-cyan-500/30 bg-cyan-500/15 text-cyan-300"
                                                                : "border-transparent text-slate-400 hover:border-cyan-500/20 hover:bg-cyan-500/10 hover:text-cyan-300"
                                                        }
                                                    `}
                                                    title="Preview report"
                                                >
                                                    <Eye className="h-4 w-4" />
                                                </button>

                                                <button
                                                    type="button"
                                                    disabled={!report.exists}
                                                    onClick={() =>
                                                        onDownload(
                                                            report.name
                                                        )
                                                    }
                                                    className="
                                                        rounded-lg
                                                        border
                                                        border-transparent
                                                        p-2
                                                        text-slate-400
                                                        transition
                                                        hover:border-cyan-500/20
                                                        hover:bg-cyan-500/10
                                                        hover:text-cyan-300
                                                        disabled:cursor-not-allowed
                                                        disabled:opacity-30
                                                    "
                                                    title="Download report"
                                                >
                                                    <Download className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
