import api from "../../lib/axios";

const dashboardService = {
  async getSummary() {
    const { data } = await api.get("/dashboard/summary");
    return data;
  },

  async getRiskDistribution() {
    const { data } = await api.get("/dashboard/risk-distribution");
    return data;
  },

  async getModelComparison() {
    const { data } = await api.get("/dashboard/model-comparison");
    return data;
  },

  async getSystemStatistics() {
    const { data } = await api.get("/dashboard/system-statistics");
    return data;
  },

  async getTopSuspicious() {
    const { data } = await api.get("/dashboard/top-suspicious");
    return data;
  },
};

export default dashboardService;
