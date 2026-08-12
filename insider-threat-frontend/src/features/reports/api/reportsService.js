import api from "../../../lib/axios";

const CANONICAL_REPORTS = [
    { name: "top_suspicious", filename: "top_suspicious.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 50 },
    { name: "top_100_suspicious", filename: "top_100_suspicious.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 100 },
    { name: "critical_employee_summary", filename: "critical_employee_summary.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 15 },
    { name: "model_comparison", filename: "model_comparison.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "model_performance", filename: "model_performance.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "performance_metrics", filename: "performance_metrics.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 14 },
    { name: "system_statistics", filename: "system_statistics.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 1000 },
    { name: "risk_level_distribution", filename: "risk_level_distribution.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 4 },
    { name: "risk_level_statistics", filename: "risk_level_statistics.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 4 },
    { name: "dataset_statistics", filename: "dataset_statistics.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 1000 },
    { name: "feature_statistics", filename: "feature_statistics.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 24 },
    { name: "feature_importance", filename: "feature_importance.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 24 },
    { name: "employee_explanations", filename: "employee_explanations.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 1000 },
    { name: "top_behavioral_factors", filename: "top_behavioral_factors.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 10 },
    { name: "consensus_summary", filename: "consensus_summary.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "model_ranking", filename: "model_ranking.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "training_times", filename: "training_times.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "training_time_ranking", filename: "training_time_ranking.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
    { name: "classification_report", filename: "classification_report.csv", exists: true, live: true, generated_at: "2011-05-31 00:00:00 UTC", record_count: 7 },
];

const reportsService = {
    // ============================================================
    // AVAILABLE REPORTS
    // ============================================================

    async getAvailableReports() {
        try {
            const { data } = await api.get("/reports/list");
            if (Array.isArray(data) && data.length > 0) {
                return data;
            }
            return CANONICAL_REPORTS;
        } catch {
            return CANONICAL_REPORTS;
        }
    },

    // ============================================================
    // ALL REPORT DATA
    // ============================================================

    async getAllReports() {
        try {
            const { data } = await api.get("/reports/all");
            if (data && typeof data === "object" && Object.keys(data).length > 0) {
                return data;
            }
        } catch {
            // Silence error and try fallback
        }

        try {
            const top100Res = await api.get("/reports/top_100_suspicious");
            const top100 = Array.isArray(top100Res.data) ? top100Res.data : [];
            return {
                top_100_suspicious: top100,
            };
        } catch {
            return {};
        }
    },

    // ============================================================
    // SINGLE REPORT
    // ============================================================

    async getReport(reportName) {
        if (!reportName) {
            return [];
        }

        try {
            const { data } = await api.get(
                `/reports/${encodeURIComponent(reportName)}`
            );
            return Array.isArray(data) ? data : [];
        } catch {
            return [];
        }
    },

    // ============================================================
    // DOWNLOAD REPORT
    // ============================================================

    async downloadReport(reportName, format = "csv") {
        if (!reportName) {
            return;
        }

        const response = await api.get(
            `/reports/download/${encodeURIComponent(reportName)}?format=${encodeURIComponent(format)}`,
            {
                responseType: "blob",
            }
        );

        const ext = format === "pdf" ? "pdf" : format === "excel" || format === "xlsx" ? "xlsx" : "csv";
        const contentType = response.headers?.["content-type"] || (ext === "pdf" ? "application/pdf" : ext === "xlsx" ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" : "text/csv;charset=utf-8");

        const blob = new Blob([response.data], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${reportName}.${ext}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    },
};

export default reportsService;
