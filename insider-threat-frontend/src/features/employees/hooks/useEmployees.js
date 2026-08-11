import { useQuery } from "@tanstack/react-query";
import employeeService from "../api/employeeService";

export const EMPLOYEE_INTELLIGENCE_QUERY_KEY = [
  "employees",
  "intelligence",
];

export const EMPLOYEE_INTELLIGENCE_SUMMARY_QUERY_KEY = [
  "employees",
  "intelligence",
  "summary",
];

export function useEmployees() {
  return useQuery({
    queryKey: EMPLOYEE_INTELLIGENCE_QUERY_KEY,
    queryFn: employeeService.getEmployeeIntelligence,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    refetchOnWindowFocus: true,
  });
}

export function useEmployeeIntelligenceSummary() {
  return useQuery({
    queryKey: EMPLOYEE_INTELLIGENCE_SUMMARY_QUERY_KEY,
    queryFn: employeeService.getEmployeeIntelligenceSummary,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    refetchOnWindowFocus: true,
  });
}

export function useEmployeeIntelligence(user, enabled = true) {
  return useQuery({
    queryKey: ["employees", "intelligence", user],
    queryFn: () =>
      employeeService.getEmployeeIntelligenceByUser(user),
    enabled: Boolean(user) && enabled,
    staleTime: 30 * 1000,
    refetchOnWindowFocus: true,
  });
}
