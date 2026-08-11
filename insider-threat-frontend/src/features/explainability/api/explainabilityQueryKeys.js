const explainabilityQueryKeys = {
  all: ["explainability"],

  featureImportance: [
    "explainability",
    "feature-importance",
  ],

  behavioralFactors: [
    "explainability",
    "top-behavioral-factors",
  ],

  employee: (employeeId) => [
    "explainability",
    "employee",
    employeeId,
  ],
};

export default explainabilityQueryKeys;
