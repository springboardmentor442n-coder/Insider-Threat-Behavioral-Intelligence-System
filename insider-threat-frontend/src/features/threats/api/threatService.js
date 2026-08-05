import api from "../../../lib/axios";

const threatService = {
  async getThreats(filters = {}) {
    const response = await api.get("/threats/", {
      params: filters,
    });

    return response.data;
  },

  async getThreat(id) {
    const response = await api.get(`/threats/${id}`);
    return response.data;
  },

  async createThreat(payload) {
    const response = await api.post("/threats/", payload);
    return response.data;
  },

  async updateThreat(id, payload) {
    const response = await api.put(
      `/threats/${id}`,
      payload
    );

    return response.data;
  },

  async resolveThreat(id) {
    const response = await api.post(
      `/threats/${id}/resolve`
    );

    return response.data;
  },

  async deleteThreat(id) {
    const response = await api.delete(
      `/threats/${id}`
    );

    return response.data;
  },
};

export default threatService;
