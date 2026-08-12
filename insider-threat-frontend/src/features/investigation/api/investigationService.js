import api from "../../../lib/axios";

/*
|--------------------------------------------------------------------------
| Investigation Service
|--------------------------------------------------------------------------
|
| Investigation and Threat Center MUST use the same canonical
| ML-derived threat intelligence.
|
| Canonical backend source:
|
|     GET /threats/
|     GET /threats/{id}
|
| Investigation only transforms the response into the shape
| required by the existing Investigation UI.
|
|--------------------------------------------------------------------------
*/

/*
|--------------------------------------------------------------------------
| Evidence normalization
|--------------------------------------------------------------------------
*/

function normalizeEvidence(evidence) {
  if (!evidence) {
    return [];
  }

  if (Array.isArray(evidence)) {
    return evidence;
  }

  if (typeof evidence === "string") {
    return [evidence];
  }

  return [String(evidence)];
}

/*
|--------------------------------------------------------------------------
| Canonical risk level
|--------------------------------------------------------------------------
|
| These thresholds MUST match the backend ML risk-scoring pipeline:
|
| 0  - <30  Low
| 30 - <60  Medium
| 60 - <80  High
| 80 - 100  Critical
|
| IMPORTANT:
| We normally use threat.risk_level directly.
| This function exists only as a safe fallback.
|--------------------------------------------------------------------------
*/

function calculateRiskLevel(score) {
  const risk = Math.max(
    0,
    Math.min(100, Number(score ?? 0))
  );

  if (risk >= 80) {
    return "Critical";
  }

  if (risk >= 60) {
    return "High";
  }

  if (risk >= 30) {
    return "Medium";
  }

  return "Low";
}

/*
|--------------------------------------------------------------------------
| Normalize Threat Center record
|--------------------------------------------------------------------------
*/

function normalizeThreat(threat) {
  if (!threat) {
    return null;
  }

  const riskScore = Number(threat.risk_score ?? 0);

  const riskLevel =
    threat.risk_level ??
    threat.severity ??
    calculateRiskLevel(riskScore);

  const employeeName =
    threat.employee_name ??
    threat.user ??
    "Unknown Employee";

  const employeeId =
    threat.employee_id ??
    threat.rank ??
    null;

  /*
  |--------------------------------------------------------------------------
  | Investigation record
  |--------------------------------------------------------------------------
  */

  return {
    /*
    |--------------------------------------------------------------------------
    | Shared identifier
    |--------------------------------------------------------------------------
    */

    id: threat.id ?? threat.rank ?? employeeId,

    /*
    |--------------------------------------------------------------------------
    | Employee identity
    |--------------------------------------------------------------------------
    */

    employee: employeeName,
    employee_name: employeeName,
    employee_id: employeeId,
    user: threat.user ?? employeeName,

    /*
    |--------------------------------------------------------------------------
    | Organization
    |--------------------------------------------------------------------------
    */

    department:
      threat.department ??
      "CERT Dataset",

    /*
    |--------------------------------------------------------------------------
    | Risk
    |--------------------------------------------------------------------------
    */

    risk_score: riskScore,

    risk_level: riskLevel,

    severity:
      threat.severity ??
      riskLevel,

    rank:
      threat.rank ??
      null,

    /*
    |--------------------------------------------------------------------------
    | Threat information
    |--------------------------------------------------------------------------
    */

    threat_type:
      threat.threat_type ??
      "Behavioral Anomaly",

    prediction:
      threat.prediction ??
      riskLevel,

    status:
      threat.status ??
      "Open",

    description:
      threat.description ??
      "No threat description available.",

    /*
    |--------------------------------------------------------------------------
    | Evidence
    |--------------------------------------------------------------------------
    */

    evidence: normalizeEvidence(
      threat.evidence
    ),

    models_triggered:
      threat.models_triggered ??
      "No models flagged",

    suspicious_count:
      Number(threat.suspicious_count ?? 0),

    consensus_percentage:
      Number(
        threat.consensus_percentage ?? 0
      ),

    weighted_score:
      Number(
        threat.weighted_score ?? 0
      ),

    /*
    |--------------------------------------------------------------------------
    | ML model predictions
    |--------------------------------------------------------------------------
    */

    isolation_forest_prediction:
      threat.isolation_forest_prediction ??
      null,

    isolation_forest_score:
      threat.isolation_forest_score ??
      null,

    one_class_svm_prediction:
      threat.one_class_svm_prediction ??
      null,

    one_class_svm_score:
      threat.one_class_svm_score ??
      null,

    lof_prediction:
      threat.lof_prediction ??
      null,

    lof_score:
      threat.lof_score ??
      null,

    elliptic_envelope_prediction:
      threat.elliptic_envelope_prediction ??
      null,

    elliptic_envelope_score:
      threat.elliptic_envelope_score ??
      null,

    pca_prediction:
      threat.pca_prediction ??
      null,

    pca_score:
      threat.pca_score ??
      null,

    dbscan_prediction:
      threat.dbscan_prediction ??
      null,

    dbscan_score:
      threat.dbscan_score ??
      null,

    kmeans_prediction:
      threat.kmeans_prediction ??
      null,

    kmeans_score:
      threat.kmeans_score ??
      null,

    /*
    |--------------------------------------------------------------------------
    | Dates
    |--------------------------------------------------------------------------
    |
    | ML-derived Threat Center records currently do not contain
    | investigation assignment/update timestamps.
    |
    | Keep these null instead of displaying "undefined".
    |--------------------------------------------------------------------------
    */

    created_at:
      threat.created_at ??
      null,

    updated_at:
      threat.updated_at ??
      null,

    assigned_to:
      threat.assigned_to ??
      null,

    notes:
      threat.notes ??
      threat.description ??
      "No investigation notes available.",

    /*
    |--------------------------------------------------------------------------
    | Complete original Threat Center record
    |--------------------------------------------------------------------------
    |
    | Keep the original object available so future Investigation
    | features can use additional ML fields without another API call.
    |--------------------------------------------------------------------------
    */

    threat,
  };
}

/*
|--------------------------------------------------------------------------
| Investigation API
|--------------------------------------------------------------------------
*/

const investigationService = {
  /*
  |--------------------------------------------------------------------------
  | Get all investigations
  |--------------------------------------------------------------------------
  |
  | IMPORTANT:
  | Investigation does NOT use the legacy static /investigation
  | demonstration cases.
  |
  | It consumes the same canonical Threat Center dataset.
  |--------------------------------------------------------------------------
  */

  async getCases() {
    try {
      const { data } = await api.get("/investigation");
      if (Array.isArray(data) && data.length > 0) {
        return data.map(normalizeThreat).filter(Boolean);
      }
    } catch (err) {
      console.warn("Fallback to /threats/ endpoint:", err);
    }

    const { data } = await api.get("/threats/");

    if (!Array.isArray(data)) {
      return [];
    }

    return data
      .map(normalizeThreat)
      .filter(Boolean);
  },

  /*
  |--------------------------------------------------------------------------
  | Create or Open investigation case
  |--------------------------------------------------------------------------
  */

  async createCase(employeeId) {
    if (!employeeId) return null;
    const { data } = await api.post(`/investigation/create/${encodeURIComponent(employeeId)}`);
    return normalizeThreat(data);
  },

  /*
  |--------------------------------------------------------------------------
  | Get one investigation
  |--------------------------------------------------------------------------
  */

  async getCase(caseId) {
    if (
      caseId === null ||
      caseId === undefined ||
      caseId === ""
    ) {
      return null;
    }

    try {
      const { data } = await api.get(`/investigation/${encodeURIComponent(caseId)}`);
      if (data) return normalizeThreat(data);
    } catch (err) {
      // fallback to threat endpoint
    }

    const { data } = await api.get(
      `/threats/${encodeURIComponent(caseId)}`
    );

    return normalizeThreat(data);
  },

  async escalateCase(caseId) {
    if (!caseId) return null;
    const { data } = await api.post(`/investigation/${encodeURIComponent(caseId)}/escalate`);
    return normalizeThreat(data);
  },

  async updateStatus(caseId, status) {
    if (!caseId) return null;
    const { data } = await api.post(`/investigation/${encodeURIComponent(caseId)}/status?status=${encodeURIComponent(status)}`);
    return normalizeThreat(data);
  },

  async assignCase(caseId, analyst) {
    if (!caseId) return null;
    const { data } = await api.post(`/investigation/${encodeURIComponent(caseId)}/assign?analyst=${encodeURIComponent(analyst)}`);
    return normalizeThreat(data);
  },

  async addNote(caseId, note) {
    if (!caseId) return null;
    const { data } = await api.post(`/investigation/${encodeURIComponent(caseId)}/notes?note=${encodeURIComponent(note)}`);
    return normalizeThreat(data);
  },
};

export default investigationService;
