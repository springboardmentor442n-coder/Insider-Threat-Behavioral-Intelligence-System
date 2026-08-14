import api from "../../lib/axios";

const employeeEvaluationService = {
  // ============================================================
  // EVALUATE (inference only — does NOT save)
  // ============================================================
  async evaluate(payload) {
    const { data } = await api.post("/employee-evaluation/evaluate", payload);
    return data;
  },

  // ============================================================
  // SAVE (persist to session store)
  // ============================================================
  async save(analysisResult) {
    const { data } = await api.post("/employee-evaluation/save", analysisResult);
    return data;
  },

  // ============================================================
  // LIST ALL EVALUATED EMPLOYEES
  // ============================================================
  async getAll() {
    const { data } = await api.get("/employee-evaluation/");
    return data;
  },

  // ============================================================
  // GET ONE EVALUATION
  // ============================================================
  async getOne(employeeId) {
    const { data } = await api.get(`/employee-evaluation/${employeeId}`);
    return data;
  },

  // ============================================================
  // DELETE EVALUATION (Administrator only)
  // ============================================================
  async deleteEvaluation(employeeId) {
    const { data } = await api.delete(`/employee-evaluation/${employeeId}`);
    return data;
  },

  // ============================================================
  // COMPARISON SUMMARY (CERT vs NEW)
  // ============================================================
  async getComparisonSummary() {
    const { data } = await api.get("/employee-evaluation/comparison/summary");
    return data;
  },

  // ============================================================
  // COMBINED RISK RANKING
  // ============================================================
  async getComparisonRanking() {
    const { data } = await api.get("/employee-evaluation/comparison/ranking");
    return data;
  },

  // ============================================================
  // INDIVIDUAL PERCENTILE COMPARISON
  // ============================================================
  async getIndividualComparison(employeeId) {
    const { data } = await api.get(`/employee-evaluation/comparison/${employeeId}`);
    return data;
  },
};

export default employeeEvaluationService;
