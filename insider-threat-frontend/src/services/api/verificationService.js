import api from "../../lib/axios";

const verificationService = {
  // ============================================================
  // CERT BEHAVIORAL PATTERN VALIDATION SUMMARY
  // ============================================================
  async getBehavioralSummary() {
    const { data } = await api.get("/verification/behavioral-summary");
    return data;
  },

  // ============================================================
  // INDIVIDUAL EMPLOYEE CERT BEHAVIORAL EVIDENCE
  // ============================================================
  async getEmployeeBehavioralEvidence(userId) {
    const { data } = await api.get(`/verification/employee/${userId}`);
    return data;
  },
};

export default verificationService;
