import Sidebar from "../components/Sidebar";

function Employee() {
  const employees = [
    { id: 1, name: "John Doe", dept: "HR", risk: "Low" },
    { id: 2, name: "Alice", dept: "Finance", risk: "Medium" },
    { id: 3, name: "David", dept: "IT", risk: "High" },
  ];

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <Sidebar />

      <div style={{ flex: 1, padding: "40px", color: "white" }}>
        <h1>Employees</h1>

        <table
          style={{
            width: "100%",
            marginTop: "30px",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr style={{ background: "#1e293b" }}>
              <th style={{ padding: "15px" }}>ID</th>
              <th>Name</th>
              <th>Department</th>
              <th>Risk Level</th>
            </tr>
          </thead>

          <tbody>
            {employees.map((emp) => (
              <tr
                key={emp.id}
                style={{
                  textAlign: "center",
                  background: "#273549",
                  borderBottom: "8px solid #0f172a",
                }}
              >
                <td style={{ padding: "15px" }}>{emp.id}</td>
                <td>{emp.name}</td>
                <td>{emp.dept}</td>
                <td>{emp.risk}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Employee;