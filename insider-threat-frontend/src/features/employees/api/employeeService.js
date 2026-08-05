import api from "../../../lib/axios";

const employeeService = {
  // ==========================================================
  // GET EMPLOYEES
  // ==========================================================
  async getEmployees(filters = {}) {
    const {
      search,
      department,
      riskLevel,
      page = 1,
      pageSize = 20,
    } = filters;

    const params = {
      page,
      page_size: pageSize,
    };

    if (search) params.search = search;
    if (department) params.department = department;
    if (riskLevel) params.risk_level = riskLevel;

    const { data } = await api.get("/employees/", {
      params,
    });

    console.log("========== EMPLOYEES ==========");
    console.log(data);
    console.log("===============================");

    // Backend returns a plain array
    if (Array.isArray(data)) {
      return {
        items: data,
        total: data.length,
      };
    }

    // Backend returns paginated object
    return {
      items: data.items ?? [],
      total: data.total ?? data.items?.length ?? 0,
    };
  },

  // ==========================================================
  // GET EMPLOYEE
  // ==========================================================
  async getEmployeeById(id) {
    const { data } = await api.get(`/employees/${id}`);
    return data;
  },

  // ==========================================================
  // CREATE
  // ==========================================================
  async createEmployee(payload) {
    const { data } = await api.post("/employees/", payload);
    return data;
  },

  // ==========================================================
  // UPDATE
  // ==========================================================
  async updateEmployee(id, payload) {
    const { data } = await api.put(`/employees/${id}`, payload);
    return data;
  },

  // ==========================================================
  // DELETE
  // ==========================================================
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

    if (Array.isArray(data)) return data;

    return data.items ?? [];
  },
};

export default employeeService;
