import {
    FileText,
    CheckCircle,
    XCircle,
    Radio,
} from "lucide-react";

export default function ReportsOverviewCards({
    reportList,
}) {
    const reports = Array.isArray(reportList)
        ? reportList
        : [];

    const total = reports.length;

    const available = reports.filter(
        (report) => report.exists
    ).length;

    const live = reports.filter(
        (report) => report.live
    ).length;

    const missing = Math.max(
        total - available,
        0
    );

    const cards = [
        {
            title: "Total Reports",
            value: total,
            icon: FileText,
        },
        {
            title: "Available",
            value: available,
            icon: CheckCircle,
        },
        {
            title: "Live",
            value: live,
            icon: Radio,
        },
        {
            title: "Missing",
            value: missing,
            icon: XCircle,
        },
    ];

    return (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {cards.map((card) => {
                const Icon = card.icon;

                return (
                    <div
                        key={card.title}
                        className="
                            rounded-2xl
                            border
                            border-cyan-500/15
                            bg-slate-900/65
                            px-4
                            py-4
                            shadow-lg
                            shadow-black/10
                        "
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs font-medium text-slate-400">
                                    {card.title}
                                </p>

                                <p className="mt-1 text-2xl font-bold text-white">
                                    {card.value}
                                </p>
                            </div>

                            <div className="rounded-xl bg-cyan-500/10 p-2.5">
                                <Icon className="h-5 w-5 text-cyan-400" />
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
