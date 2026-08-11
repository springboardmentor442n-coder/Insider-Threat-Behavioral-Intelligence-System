import { useQuery } from "@tanstack/react-query";

import dashboardService from "../../services/api/dashboardService";
import threatService from "../../features/threats/api/threatService";

// ============================================================
// DASHBOARD QUERY KEYS
// ============================================================

export const dashboardQueryKeys = {
  all: ["dashboard"],

  summary: () => [
    "dashboard",
    "summary",
  ],

  riskDistribution: () => [
    "dashboard",
    "risk-distribution",
  ],

  modelComparison: () => [
    "dashboard",
    "model-comparison",
  ],

  systemStatistics: () => [
    "dashboard",
    "system-statistics",
  ],

  topSuspicious: () => [
    "dashboard",
    "top-suspicious",
  ],
};

// ============================================================
// LIVE QUERY OPTIONS
// ============================================================
//
// Dashboard should behave like Threat Center.
// Threat Center already refreshes every 10 seconds.
//
// This keeps the entire application reasonably live without
// hammering the backend continuously.
// ============================================================

const liveQueryOptions = {
  staleTime: 10 * 1000,

  refetchInterval: 10 * 1000,

  refetchOnReconnect: true,

  refetchOnMount: true,

  refetchOnWindowFocus: true,

  retry: 2,
};

// ============================================================
// DASHBOARD SUMMARY
// ============================================================

export function useDashboard() {
  return useQuery({
    queryKey: dashboardQueryKeys.summary(),

    queryFn: dashboardService.getSummary,

    ...liveQueryOptions,
  });
}

// ============================================================
// RISK DISTRIBUTION
// ============================================================

export function useRiskDistribution() {
  return useQuery({
    queryKey:
      dashboardQueryKeys.riskDistribution(),

    queryFn:
      dashboardService.getRiskDistribution,

    ...liveQueryOptions,
  });
}

// ============================================================
// MODEL COMPARISON
// ============================================================

export function useModelComparison() {
  return useQuery({
    queryKey:
      dashboardQueryKeys.modelComparison(),

    queryFn:
      dashboardService.getModelComparison,

    ...liveQueryOptions,
  });
}

// ============================================================
// SYSTEM STATISTICS
// ============================================================

export function useSystemStatistics() {
  return useQuery({
    queryKey:
      dashboardQueryKeys.systemStatistics(),

    queryFn:
      dashboardService.getSystemStatistics,

    ...liveQueryOptions,
  });
}

// ============================================================
// TOP SUSPICIOUS EMPLOYEES
// ============================================================
//
// IMPORTANT:
//
// Do NOT use /dashboard/top-suspicious.
//
// The Dashboard endpoint was producing a different risk
// representation, which is why AJF0370 appeared as:
//
//     Dashboard       71.77
//     Investigation  100
//
// The canonical Threat Center source is:
//
//     /threats/
//
// Threat Center already consumes this source.
//
// Therefore Dashboard now consumes the SAME source.
//
// Result:
//
//     AJF0370 -> 100
//
// ============================================================

export function useTopSuspicious() {
  return useQuery({
    queryKey:
      dashboardQueryKeys.topSuspicious(),

    queryFn: async () => {
      const data =
        await threatService.getThreats();

      if (!Array.isArray(data)) {
        return [];
      }

      return [...data]
        .filter(
          (employee) =>
            Number(
              employee?.risk_score ?? 0
            ) >= 0
        )
        .sort(
          (a, b) =>
            Number(
              b?.risk_score ?? 0
            ) -
            Number(
              a?.risk_score ?? 0
            )
        );
    },

    ...liveQueryOptions,
  });
}
