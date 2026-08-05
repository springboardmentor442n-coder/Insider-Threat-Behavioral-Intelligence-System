// src/features/employees/components/EmployeeRow.jsx
import { MoreVertical, Eye, Pencil, Trash2 } from 'lucide-react';
import { useState } from 'react';
import RiskBadge from './RiskBadge';

/**
 * @param {{
 *   employee: object,
 *   onView: (employee: object) => void,
 *   onEdit: (employee: object) => void,
 *   onDelete: (employee: object) => void,
 * }} props
 */
export default function EmployeeRow({ employee, onView, onEdit, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const {
    employee_code,
    full_name,
    email,
    department,
    designation,
    risk_score,
    risk_level,
  } = employee;

  return (
    <tr
      className="group cursor-pointer border-b border-white/5 transition-colors hover:bg-white/[0.03]"
      onClick={() => onView(employee)}
    >
      <td className="px-4 py-3 text-sm text-zinc-400">{employee_code}</td>
      <td className="px-4 py-3">
        <div className="text-sm font-medium text-zinc-100">{full_name}</div>
        <div className="text-xs text-zinc-500">{email}</div>
      </td>
      <td className="px-4 py-3 text-sm text-zinc-300">{department}</td>
      <td className="px-4 py-3 text-sm text-zinc-400">{designation}</td>
      <td className="px-4 py-3">
        <RiskBadge level={risk_level} score={risk_score} />
      </td>
      <td className="px-4 py-3 text-right">
        <div className="relative inline-block" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="rounded-md p-1.5 text-zinc-400 hover:bg-white/10 hover:text-white"
          >
            <MoreVertical size={16} />
          </button>
          {menuOpen && (
            <div
              className="absolute right-0 z-20 mt-1 w-36 overflow-hidden rounded-lg border border-white/10 bg-zinc-900 shadow-xl"
              onMouseLeave={() => setMenuOpen(false)}
            >
              <button
                onClick={() => { onView(employee); setMenuOpen(false); }}
                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-zinc-300 hover:bg-white/5"
              >
                <Eye size={14} /> View
              </button>
              <button
                onClick={() => { onEdit(employee); setMenuOpen(false); }}
                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-zinc-300 hover:bg-white/5"
              >
                <Pencil size={14} /> Edit
              </button>
              <button
                onClick={() => { onDelete(employee); setMenuOpen(false); }}
                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10"
              >
                <Trash2 size={14} /> Delete
              </button>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
}
