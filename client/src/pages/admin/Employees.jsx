import { ArrowBack } from "@mui/icons-material";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import EmployeeCard from "../../components/EmpoyeeCard.jsx";
import "./Employees.css";

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
      console.log(data);

      setEmployees(
        data.map((emp) => ({
          ...emp,
          qr_code_data: emp.qr_code,
        }))
      );
    } catch (error) {
      console.error("Error fetching employees:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="employees-container">
      <div className="employees-header">
        <div className="button" onClick={() => navigate("/admin/dashboard")}>
          <ArrowBack />
        </div>
        <div>
          <h1>Manage your employees</h1>
          <p className="subtitle">
            you can delete, modify or dance on the barrows of your employees, oh
            Lord of Metinna, Ebbing, Gemmera and Sovereign of Nazair and
            Vicovaro
          </p>
        </div>
      </div>

      <div className="employees-list">
        {employees.map((emp) => (
          <EmployeeCard key={emp.id} employee={emp} />
        ))}
      </div>

      {employees.length === 0 && <p>No employees found</p>}
    </div>
  );
};

export default Employees;
