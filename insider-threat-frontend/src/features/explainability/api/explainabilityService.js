import api from "../../../lib/axios";

const explainabilityService = {
  async getFeatureImportance() {
    const { data } = await api.get(
      "/explainability/feature-importance"
    );

    return data;
  },

  async getTopBehavioralFactors() {
    const { data } = await api.get(
      "/explainability/top-behavioral-factors"
    );

    return data;
  },

  async getEmployeeExplanation(employeeId) {
    const { data } = await api.get(
      `/explainability/${employeeId}`
    );

    return data;
  },
};

export default explainabilityService;
