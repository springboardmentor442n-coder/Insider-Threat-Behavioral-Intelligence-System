import api from "../../../lib/axios";

const reportsService = {
    // ============================================================
    // AVAILABLE REPORTS
    // ============================================================

    async getAvailableReports() {
        const { data } = await api.get("/reports/list");

        return Array.isArray(data) ? data : [];
    },

    // ============================================================
    // ALL REPORT DATA
    // ============================================================

    async getAllReports() {
        const { data } = await api.get("/reports/all");

        return data && typeof data === "object"
            ? data
            : {};
    },

    // ============================================================
    // SINGLE REPORT
    // ============================================================

    async getReport(reportName) {
        if (!reportName) {
            return [];
        }

        const { data } = await api.get(
            `/reports/${encodeURIComponent(reportName)}`
        );

        return Array.isArray(data) ? data : [];
    },

    // ============================================================
    // DOWNLOAD REPORT
    // ============================================================

    async downloadReport(reportName) {
        if (!reportName) {
            return;
        }

        const response = await api.get(
            `/reports/download/${encodeURIComponent(reportName)}`,
            {
                responseType: "blob",
            }
        );

        const blob = new Blob(
            [response.data],
            {
                type:
                    response.headers?.["content-type"] ||
                    "text/csv;charset=utf-8",
            }
        );

        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = url;

        link.download = `${reportName}.csv`;

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);
    },
};

export default reportsService;
