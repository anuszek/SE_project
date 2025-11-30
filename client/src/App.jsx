import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/admin/Dashboard";
import Employees from "./pages/admin/Employees";
import Reports from "./pages/admin/Reports";
import Login from "./pages/Login";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/admin/dashboard" element={<Dashboard />} />
          <Route path="/admin/employees" element={<Employees />} />
          <Route path="/admin/reports" element={<Reports />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
