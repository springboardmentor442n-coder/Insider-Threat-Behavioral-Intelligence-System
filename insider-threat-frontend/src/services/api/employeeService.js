import api from "../../lib/axios";

export const employeeService = {

  async getAllEmployees() {
    const response = await api.get("/employees");
    return response.data;
  },

  async getEmployee(id) {
    const response = await api.get(`/employees/${id}`);
    return response.data;
  },

  async createEmployee(employee) {
    const response = await api.post("/employees", employee);
    return response.data;
  },

  async updateEmployee(id, employee) {
    const response = await api.put(`/employees/${id}`, employee);
    return response.data;
  },

  async deleteEmployee(id) {
    const response = await api.delete(`/employees/${id}`);
    return response.data;
  }

};

export default employeeService;
