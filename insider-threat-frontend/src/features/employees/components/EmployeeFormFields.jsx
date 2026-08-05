import { AlertCircle } from "lucide-react";

export const DEPARTMENTS = [
  "Engineering",
  "Finance",
  "Human Resources",
  "IT Operations",
  "Legal",
  "Sales",
  "Security",
];

export const RISK_LEVELS = ["low", "medium", "high", "critical"];

export function validateEmployeeForm(values) {
  const errors = {};

  if (!values.full_name?.trim()) {
    errors.full_name = "Full name is required.";
  } else if (values.full_name.trim().length < 2) {
    errors.full_name = "Full name must be at least 2 characters.";
  }

  if (!values.email?.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "Enter a valid email address.";
  }

  if (!values.employee_code?.trim()) {
    errors.employee_code = "Employee code is required.";
  }

  if (!values.department) {
    errors.department = "Select a department.";
  }

  if (!values.designation?.trim()) {
    errors.designation = "Designation is required.";
  }

  if (
    values.risk_score === "" ||
    values.risk_score === null ||
    values.risk_score === undefined ||
    Number.isNaN(Number(values.risk_score))
  ) {
    errors.risk_score = "Risk score is required.";
  } else if (Number(values.risk_score) < 0 || Number(values.risk_score) > 100) {
    errors.risk_score = "Risk score must be between 0 and 100.";
  }

  return errors;
}

function FieldError({ message }) {
  if (!message) return null;
  return (
    <p className="mt-1 flex items-center gap-1 text-xs text-red-400">
      <AlertCircle className="h-3.5 w-3.5" />
      {message}
    </p>
  );
}

export default function EmployeeFormFields({ values, errors, onChange, disabled }) {
  const handle = (field) => (e) => onChange(field, e.target.value);

  const inputClass = (field) =>
    `w-full rounded-lg border bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:ring-2 focus:ring-cyan-500/40 ${
      errors[field]
        ? "border-red-500/60 focus:border-red-500"
        : "border-slate-700 focus:border-cyan-500/60"
    }`;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Full name
        </label>
        <input
          type="text"
          value={values.full_name}
          onChange={handle("full_name")}
          disabled={disabled}
          placeholder="Jordan Ellis"
          className={inputClass("full_name")}
        />
        <FieldError message={errors.full_name} />
      </div>

      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Employee code
        </label>
        <input
          type="text"
          value={values.employee_code}
          onChange={handle("employee_code")}
          disabled={disabled}
          placeholder="EMP-10432"
          className={inputClass("employee_code")}
        />
        <FieldError message={errors.employee_code} />
      </div>

      <div className="sm:col-span-2">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Email
        </label>
        <input
          type="email"
          value={values.email}
          onChange={handle("email")}
          disabled={disabled}
          placeholder="jordan.ellis@company.com"
          className={inputClass("email")}
        />
        <FieldError message={errors.email} />
      </div>

      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Department
        </label>
        <select
          value={values.department}
          onChange={handle("department")}
          disabled={disabled}
          className={inputClass("department")}
        >
          <option value="">Select department</option>
          {DEPARTMENTS.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>
        <FieldError message={errors.department} />
      </div>

      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Designation
        </label>
        <input
          type="text"
          value={values.designation}
          onChange={handle("designation")}
          disabled={disabled}
          placeholder="Senior Analyst"
          className={inputClass("designation")}
        />
        <FieldError message={errors.designation} />
      </div>

      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Risk score (0–100)
        </label>
        <input
          type="number"
          min="0"
          max="100"
          value={values.risk_score}
          onChange={handle("risk_score")}
          disabled={disabled}
          placeholder="42"
          className={inputClass("risk_score")}
        />
        <FieldError message={errors.risk_score} />
      </div>

      <div className="sm:col-span-1">
        <label className="mb-1 block text-xs font-medium text-slate-400">
          Risk level
        </label>
        <select
          value={values.risk_level}
          onChange={handle("risk_level")}
          disabled={disabled}
          className={inputClass("risk_level")}
        >
          {RISK_LEVELS.map((level) => (
            <option key={level} value={level}>
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
