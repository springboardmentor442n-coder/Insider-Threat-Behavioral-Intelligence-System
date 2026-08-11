import api from "../../../lib/axios";

const analyticsService = {

  // ============================================================
  // Model Comparison
  // ============================================================

  async getModelComparison() {

    const { data } = await api.get("/analytics/model-performance");

    return data.map((item) => ({
      model: item["Model"],
      accuracy: item["Detection Rate (%)"],
      trainingTime: item["Training Time (sec)"],
      suspiciousEmployees: item["Suspicious Employees"],
      averageRisk: item["Average Risk Score"],
    }));

  },

  // ============================================================
  // Training Times
  // ============================================================

  async getTrainingTimes() {

    const { data } = await api.get("/analytics/training-times");

    return data.map((item) => ({
      model: item["Model"],
      trainingTime: item["Training Time"],
    }));

  },

  // ============================================================
  // Risk Distribution
  // ============================================================

  async getRiskDistribution() {

    const { data } = await api.get("/analytics/risk-statistics");

    return data.map((item) => ({
      level: item["Risk Level"],
      count: item["Employees"],
      percentage: item["Percentage"],
    }));

  },

  // ============================================================
  // Dataset Statistics
  // ============================================================

  async getDatasetStatistics() {

    const { data } = await api.get("/analytics/dataset-statistics");

    return data;

  },

  // ============================================================
  // Feature Statistics
  // ============================================================

  async getFeatureStatistics() {

    const { data } = await api.get("/analytics/feature-statistics");

    return data.map((item) => ({
      feature: item["Unnamed: 0"],
      mean: item.mean,
      max: item.max,
      min: item.min,
    }));

  },

  // ============================================================
  // Export Analytics Report
  // ============================================================

  async exportAnalytics() {

    const response = await api.get(
      "/analytics/export",
      {
        responseType: "blob",
      }
    );

    const blob = new Blob(
      [response.data],
      {
        type: "application/zip",
      }
    );

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    link.setAttribute(
      "download",
      "Analytics_Report.zip"
    );

    document.body.appendChild(link);

    link.click();

    setTimeout(() => {

      window.URL.revokeObjectURL(url);

      document.body.removeChild(link);

    }, 100);

  },

};

export default analyticsService;
