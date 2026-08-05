import { useMemo, useState } from "react";

import { useEmployees } from "../hooks/useEmployees";

import EmployeeToolbar from "../components/EmployeeToolbar";
import EmployeeTable from "../components/EmployeeTable";
import EmployeeOverviewCards from "../components/EmployeeOverviewCards";

import EmployeeProfileDrawer from "../components/EmployeeProfileDrawer";
import AddEmployeeDialog from "../components/AddEmployeeDialog";
import EditEmployeeDialog from "../components/EditEmployeeDialog";
import DeleteEmployeeDialog from "../components/DeleteEmployeeDialog";

export default function EmployeesPage() {
  const {
    data = [],
    isLoading,
    isError,
    error,
  } = useEmployees();

  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [riskLevel, setRiskLevel] = useState("");

  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [deletingEmployee, setDeletingEmployee] = useState(null);
  const [showAddDialog, setShowAddDialog] = useState(false);

  // Supports both API formats
  const employees = Array.isArray(data)
    ? data
    : Array.isArray(data?.items)
    ? data.items
    : [];

  const filteredEmployees = useMemo(() => {
    return employees.filter((emp) => {
      const matchesSearch =
        emp.full_name?.toLowerCase().includes(search.toLowerCase()) ||
        emp.employee_code?.toLowerCase().includes(search.toLowerCase()) ||
        emp.email?.toLowerCase().includes(search.toLowerCase());

      const matchesDepartment =
        !department || emp.department === department;

      const matchesRisk =
        !riskLevel ||
        emp.risk_level?.toLowerCase() === riskLevel.toLowerCase();

      return (
        matchesSearch &&
        matchesDepartment &&
        matchesRisk
      );
    });
  }, [employees, search, department, riskLevel]);

  if (isLoading) {
    return (
      <div className="p-8 text-slate-400">
        Loading Employees...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 text-red-500">
        {error?.message || "Unable to load employees."}
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6">

        <EmployeeOverviewCards
          employees={filteredEmployees}
        />

        <EmployeeToolbar
          search={search}
          setSearch={setSearch}
          department={department}
          setDepartment={setDepartment}
          riskLevel={riskLevel}
          setRiskLevel={setRiskLevel}
          employees={filteredEmployees}
          onAdd={() => setShowAddDialog(true)}
        />

        <EmployeeTable
          employees={filteredEmployees}
          onRowClick={(employee) => {
            setSelectedEmployee(employee);
          }}
          onEdit={(employee) => {
            setEditingEmployee(employee);
          }}
          onDelete={(employee) => {
            setDeletingEmployee(employee);
          }}
        />

      </div>

      {/* Employee Profile */}

      <EmployeeProfileDrawer
        open={!!selectedEmployee}
        employee={selectedEmployee}
        onClose={() => setSelectedEmployee(null)}
        onEdit={(employee) => {
          setSelectedEmployee(null);
          setEditingEmployee(employee);
        }}
        onDelete={(employee) => {
          setSelectedEmployee(null);
          setDeletingEmployee(employee);
        }}
      />

      {/* Add Employee */}

      <AddEmployeeDialog
        open={showAddDialog}
        onClose={() => setShowAddDialog(false)}
      />

      {/* Edit Employee */}

      <EditEmployeeDialog
        open={!!editingEmployee}
        employee={editingEmployee}
        onClose={() => setEditingEmployee(null)}
      />

      {/* Delete Employee */}

      <DeleteEmployeeDialog
        open={!!deletingEmployee}
        employee={deletingEmployee}
        onClose={() => setDeletingEmployee(null)}
      />

    </>
  );
}
