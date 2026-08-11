import { useQuery } from "@tanstack/react-query";
import api from "../../lib/axios";

// ============================================================
// QUERY KEYS
// ============================================================

export const employeeQueryKeys = {
  all: ["employees"],

  intelligence: () => [
    "employees",
    "intelligence",
  ],

  intelligenceSummary: () => [
    "employees",
    "intelligence",
    "summary",
  ],

  intelligenceEmployee: (user) => [
    "employees",
    "intelligence",
    user,
  ],
};

// ============================================================
// GET ALL ML EMPLOYEES
// ============================================================

async function fetchEmployeeIntelligence() {
  const { data } = await api.get(
    "/employees/intelligence"
  );

  if (!Array.isArray(data)) {
    return [];
  }

  return data;
}

// ============================================================
// GET ML SUMMARY
// ============================================================

async function fetchEmployeeIntelligenceSummary() {
  const { data } = await api.get(
    "/employees/intelligence/summary"
  );

  return data;
}

// ============================================================
// GET SINGLE ML EMPLOYEE
// ============================================================

async function fetchEmployeeIntelligenceByUser(user) {
  const { data } = await api.get(
    `/employees/intelligence/${encodeURIComponent(user)}`
  );

  return data;
}

// ============================================================
// ALL ML EMPLOYEES
// ============================================================

export function useEmployees() {
  return useQuery({
    queryKey: employeeQueryKeys.intelligence(),

    queryFn: fetchEmployeeIntelligence,

    staleTime: 30 * 1000,

    refetchInterval: 30 * 1000,

    refetchOnWindowFocus: true,

    retry: 2,
  });
}

// ============================================================
// ML SUMMARY
// ============================================================

export function useEmployeeIntelligenceSummary() {
  return useQuery({
    queryKey:
      employeeQueryKeys.intelligenceSummary(),

    queryFn: fetchEmployeeIntelligenceSummary,

    staleTime: 30 * 1000,

    refetchInterval: 30 * 1000,

    refetchOnWindowFocus: true,

    retry: 2,
  });
}

// ============================================================
// SINGLE ML EMPLOYEE
// ============================================================

export function useEmployeeIntelligence(user) {
  return useQuery({
    queryKey:
      employeeQueryKeys.intelligenceEmployee(user),

    queryFn: () =>
      fetchEmployeeIntelligenceByUser(user),

    enabled: Boolean(user),

    staleTime: 30 * 1000,

    refetchOnWindowFocus: true,

    retry: 2,
  });
}
