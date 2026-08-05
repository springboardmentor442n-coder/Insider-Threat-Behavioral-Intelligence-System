import { useQuery } from "@tanstack/react-query";
import dashboardService from "../../services/api/dashboardService";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: dashboardService.getSummary,
    staleTime: 60000,
  });
}

export function useRiskDistribution() {
  return useQuery({
    queryKey: ["risk-distribution"],
    queryFn: dashboardService.getRiskDistribution,
  });
}

export function useModelComparison() {
  return useQuery({
    queryKey: ["model-comparison"],
    queryFn: dashboardService.getModelComparison,
  });
}

export function useSystemStatistics() {
  return useQuery({
    queryKey: ["system-statistics"],
    queryFn: dashboardService.getSystemStatistics,
  });
}

export function useTopSuspicious() {
  return useQuery({
    queryKey: ["top-suspicious"],
    queryFn: dashboardService.getTopSuspicious,
  });
}
