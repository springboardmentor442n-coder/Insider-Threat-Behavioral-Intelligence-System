import api from "../../lib/axios";

const dashboardService = {
  // ============================================================
  // SUMMARY
  // ============================================================

  async getSummary() {
    const { data } =
      await api.get("/dashboard/summary");

    return data;
  },

  // ============================================================
  // RISK DISTRIBUTION
  // ============================================================

  async getRiskDistribution() {
    const { data } =
      await api.get(
        "/dashboard/risk-distribution"
      );

    return data;
  },

  // ============================================================
  // MODEL COMPARISON
  // ============================================================

  async getModelComparison() {
    const { data } =
      await api.get(
        "/dashboard/model-comparison"
      );

    return data;
  },

  // ============================================================
  // SYSTEM STATISTICS
  // ============================================================

  async getSystemStatistics() {
    const { data } =
      await api.get(
        "/dashboard/system-statistics"
      );

    return data;
  },
};

export default dashboardService;
