import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Employee from "./pages/Employee";
import Predictions from "./pages/Predictions";
import BehaviorProfile from "./pages/BehaviorProfile";
import Pipeline from "./pages/Pipeline";
import EmployeeDetails from "./pages/EmployeeDetails";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/employees" element={<Employee />} />

        <Route path="/predictions" element={<Predictions />} />

        <Route
          path="/behavior-profile"
          element={<BehaviorProfile />}
        />

        <Route
          path="/pipeline"
          element={<Pipeline />}
        />
        <Route
          path="/employee/:employee_id"
          element={<EmployeeDetails />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;