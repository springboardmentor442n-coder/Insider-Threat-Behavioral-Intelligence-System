/*
|--------------------------------------------------------------------------
| Investigation Query Keys
|--------------------------------------------------------------------------
|
| Investigation data comes from the same canonical threat source as
| Threat Center.
|
| We still keep a separate React Query namespace for Investigation
| because the UI representation is different.
|
|--------------------------------------------------------------------------
*/

const investigationQueryKeys = {
  all: ["investigation"],

  cases: () => [
    "investigation",
    "cases",
  ],

  details: (caseId) => [
    "investigation",
    "case",
    caseId,
  ],
};

export default investigationQueryKeys;
