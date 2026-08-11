import { Download, RefreshCcw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import analyticsService from "../api/analyticsService";

export default function AnalyticsToolbar() {

    const queryClient = useQueryClient();

    // ===========================================================
    // Refresh Analytics
    // ===========================================================

    const handleRefresh = async () => {

        try {

            console.log("Refreshing Analytics...");

            await queryClient.refetchQueries({

                queryKey: ["analytics"],

            });

            console.log("Analytics refreshed successfully.");

        }

        catch (error) {

            console.error("Refresh failed:", error);

        }

    };

    // ===========================================================
    // Export Analytics Reports
    // ===========================================================

    const handleExport = async () => {

        try {

            await analyticsService.exportAnalytics();

            console.log("Analytics exported successfully.");

        }

        catch (error) {

            console.error("Export failed:", error);

        }

    };

    return (

        <div className="flex items-center justify-between rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-4">

            <div>

                <h2 className="text-xl font-semibold text-white">

                    Analytics Dashboard

                </h2>

                <p className="mt-1 text-sm text-slate-400">

                    Machine Learning performance, department risk,
                    behavioural trends and anomaly statistics.

                </p>

            </div>

            <div className="flex gap-3">

                <button

                    onClick={handleRefresh}

                    className="flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-cyan-300 transition hover:bg-cyan-500/20"

                >

                    <RefreshCcw size={18} />

                    Refresh

                </button>

                <button

                    onClick={handleExport}

                    className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-emerald-300 transition hover:bg-emerald-500/20"

                >

                    <Download size={18} />

                    Export

                </button>

            </div>

        </div>

    );

}
