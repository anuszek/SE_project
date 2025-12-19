import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Employees.css";
import { ArrowBack } from "@mui/icons-material";

const Employees = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/employees/all");
      const data = await response.json();
      setEmployees(data);
    } catch (error) {
      console.error("Error fetching employees:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="employees-container">
      <div style={{ marginBottom: "2rem" }}>
        <button 
          onClick={() => navigate("/admin/dashboard")}
          style={{ marginRight: "1rem" }}
        >
          ← Back
        </button>
        <h1>Employees List</h1>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
        {employees.map((emp) => (
          <div key={emp.id} style={{ 
            background: "white", 
            padding: "1.5rem", 
            borderRadius: "8px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
          }}>
            <h3>{emp.first_name} {emp.last_name}</h3>
            <p><strong>Email:</strong> {emp.email}</p>
            <p><strong>ID:</strong> {emp.id}</p>
            <p><strong>Added:</strong> {new Date(emp.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>

      {employees.length === 0 && <p>No employees found</p>}
    </div>
  );
};

export default Employees;
