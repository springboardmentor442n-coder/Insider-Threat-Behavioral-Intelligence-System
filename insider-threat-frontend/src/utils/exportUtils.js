/**
 * Export utilities for the Employee module.
 *
 * Excel export uses SheetJS (`xlsx`), which is the standard client-side
 * library for generating real .xlsx files. Install it if not already present:
 *
 *   npm install xlsx
 */
import * as XLSX from "xlsx";

const EXPORT_COLUMNS = [
  { key: "employee_code", label: "Employee Code" },
  { key: "full_name", label: "Full Name" },
  { key: "email", label: "Email" },
  { key: "department", label: "Department" },
  { key: "designation", label: "Designation" },
  { key: "risk_score", label: "Risk Score" },
  { key: "risk_level", label: "Risk Level" },
  { key: "created_at", label: "Created At" },
];

function toRows(employees) {
  return employees.map((emp) =>
    EXPORT_COLUMNS.reduce((row, col) => {
      row[col.label] = emp[col.key] ?? "";
      return row;
    }, {})
  );
}

function timestampedFilename(base, ext) {
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  return `${base}_${stamp}.${ext}`;
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function escapeCsvValue(value) {
  const str = String(value ?? "");
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

export function exportEmployeesToCsv(employees, filenameBase = "employees") {
  if (!employees?.length) return;

  const rows = toRows(employees);
  const header = EXPORT_COLUMNS.map((c) => c.label).join(",");
  const body = rows
    .map((row) =>
      EXPORT_COLUMNS.map((c) => escapeCsvValue(row[c.label])).join(",")
    )
    .join("\n");

  const csvContent = `${header}\n${body}`;
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  triggerDownload(blob, timestampedFilename(filenameBase, "csv"));
}

export function exportEmployeesToExcel(employees, filenameBase = "employees") {
  if (!employees?.length) return;

  const rows = toRows(employees);
  const worksheet = XLSX.utils.json_to_sheet(rows);

  // Reasonable default column widths so the sheet is readable on open.
  worksheet["!cols"] = EXPORT_COLUMNS.map((c) => ({
    wch: Math.max(c.label.length + 2, 16),
  }));

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Employees");

  const arrayBuffer = XLSX.write(workbook, {
    bookType: "xlsx",
    type: "array",
  });
  const blob = new Blob([arrayBuffer], {
    type: "application/octet-stream",
  });
  triggerDownload(blob, timestampedFilename(filenameBase, "xlsx"));
}
