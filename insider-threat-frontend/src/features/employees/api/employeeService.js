import api from "../../../lib/axios";

const employeeService = {
  // ==========================================================
  // CERT ML EMPLOYEE INTELLIGENCE
  // ==========================================================

  async getEmployeeIntelligence() {
    const { data } = await api.get("/employees/intelligence");

    if (!Array.isArray(data)) {
      return [];
    }

    return data;
  },

  // ==========================================================
  // CERT ML EMPLOYEE SUMMARY
  // ==========================================================

  async getEmployeeIntelligenceSummary() {
    const { data } = await api.get("/employees/intelligence/summary");

    return data;
  },

  // ==========================================================
  // SINGLE CERT EMPLOYEE INTELLIGENCE
  // ==========================================================

  async getEmployeeIntelligenceByUser(user) {
    const { data } = await api.get(
      `/employees/intelligence/${encodeURIComponent(user)}`
    );

    return data;
  },

  // ==========================================================
  // EXISTING APPLICATION EMPLOYEE CRUD
  // Keep these available for the existing CRUD workflow.
  // ==========================================================

  async getEmployees() {
    const { data } = await api.get("/employees/");

    return Array.isArray(data) ? data : [];
  },

  async getEmployeeById(id) {
    const { data } = await api.get(`/employees/${id}`);

    return data;
  },

  async createEmployee(payload) {
    const { data } = await api.post("/employees/", payload);

    return data;
  },

  async updateEmployee(id, payload) {
    const { data } = await api.put(`/employees/${id}`, payload);

    return data;
  },

  async deleteEmployee(id) {
    const { data } = await api.delete(`/employees/${id}`);

    return data;
  },

  // ==========================================================
  // ACTIVITY
  // ==========================================================

  async getEmployeeActivity(id) {
    const { data } = await api.get("/activity/", {
      params: {
        employee_id: id,
      },
    });

    if (Array.isArray(data)) {
      return data;
    }

    return data.items ?? [];
  },
};

export default employeeService;
