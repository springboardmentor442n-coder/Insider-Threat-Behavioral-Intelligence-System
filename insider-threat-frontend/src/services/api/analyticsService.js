import api from "../../lib/axios";

const analyticsService = {
  async getRiskDistribution() {
    const { data } = await api.get("/dashboard/risk-distribution");
    return data;
  },

  async getModelComparison() {
    const { data } = await api.get("/dashboard/model-comparison");
    return data;
  },

  async getTopSuspicious() {
    const { data } = await api.get("/dashboard/top-suspicious");
    return data;
  },

  async getSystemStatistics() {
    const { data } = await api.get("/dashboard/system-statistics");
    return data;
  },
};

export default analyticsService;
