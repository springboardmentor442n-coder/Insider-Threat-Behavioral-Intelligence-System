/**
 * Shared formatting utilities for displaying numeric data cleanly.
 * DOES NOT modify raw backend precision or export data precision.
 */

/**
 * Format a number as percentage (e.g., 28.57%).
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined || value === "") return "0.00%";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "0.00%";
  return `${numeric.toFixed(decimals)}%`;
}

/**
 * Format a risk score (0-100, e.g., 96.50 or 100.00).
 */
export function formatScore(value, decimals = 2) {
  if (value === null || value === undefined || value === "") return "0.00";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "0.00";
  return numeric.toFixed(decimals);
}

/**
 * Format general floating-point or integer numbers with thousands separators (e.g. 22,551.71).
 */
export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || value === "") return "0";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);

  if (Number.isInteger(numeric)) {
    return numeric.toLocaleString();
  }

  return numeric.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format decimal numbers, automatically choosing precision for small decimals vs larger floats.
 */
export function formatDecimal(value, defaultDecimals = 2) {
  if (value === null || value === undefined || value === "") return "0";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);

  if (Math.abs(numeric) > 0 && Math.abs(numeric) < 0.01) {
    return numeric.toFixed(4);
  }
  return numeric.toLocaleString(undefined, {
    minimumFractionDigits: defaultDecimals,
    maximumFractionDigits: defaultDecimals,
  });
}

/**
 * Defensive date formatter to prevent 1/1/1970 rendering.
 */
export function formatDate(value, fallback = "Unknown") {
  if (!value || value === "0" || value === 0) return fallback;
  const d = new Date(value);
  if (Number.isNaN(d.getTime()) || d.getFullYear() <= 1970) return fallback;
  return d.toLocaleDateString();
}

/**
 * Cleanly format feature/column names from snake_case to human-readable title case.
 */
export function formatFeatureName(name) {
  if (!name || typeof name !== "string") return "N/A";

  const featureMap = {
    total_events: "Total Event Volume",
    midnight_activity_count: "Midnight Activity",
    usb_after_hours_count: "After-Hours USB Usage",
    file_copy_count: "File Export Volume",
    email_external_count: "External Emails",
    pc_access_count: "Multi-PC Logons",
    http_job_search_count: "Job Search Web Traffic",
    suspicious_count: "Models Flagged Count",
    weighted_score: "Weighted Risk Score",
    consensus_percentage: "Consensus Percentage",
  };

  const clean = name.trim().toLowerCase();
  if (featureMap[clean]) {
    return featureMap[clean];
  }

  return name
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
