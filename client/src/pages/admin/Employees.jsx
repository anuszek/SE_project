import { ArrowBack, Close } from "@mui/icons-material";
import {
  FormControl,
  InputLabel,
  OutlinedInput,
  TextField,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  deleteEmployee,
  fetchEmployees,
  generateNewQR,
  inactivateQR,
  modifyEmployee,
} from "../../api/employees.js";
import EmployeeCard from "../../components/EmpoyeeCard.jsx";
import "./Employees.css";

const Employees = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState(null);

  useEffect(() => {
    getEmployees();
  }, []);

  const getEmployees = async () => {
    try {
      const data = await fetchEmployees();

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

  const handleDelete = async (employeeId) => {
    try {
      await deleteEmployee(employeeId);
      setEmployees(employees.filter((emp) => emp.id !== employeeId));
    } catch (error) {
      console.error("Error deleting employee:", error);
    }
  };

  const showModify = (employeeData) => {
    setEditing(true);
    setCurrentEmployee(employeeData);
  };

  const handleModify = async (employeeData) => {
    try {
      const updatedEmployee = await modifyEmployee(employeeData);
      setEmployees(
        employees.map((emp) =>
          emp.id === updatedEmployee.id
            ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
            : emp
        )
      );
    } catch (error) {
      console.error("Error modifying employee:", error);
    }
  };

  const handleGenerateNewQR = async (employeeId) => {
    try {
      const updatedEmployee = await generateNewQR(employeeId);
      setEmployees(
        employees.map((emp) =>
          emp.id === updatedEmployee.id
            ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
            : emp
        )
      );
    } catch (error) {
      console.error("Error generating new QR code:", error);
    }
  };

  const handleInactivateQR = async (employeeId) => {
    try {
      const updatedEmployee = await inactivateQR(employeeId);
      setEmployees(
        employees.map((emp) =>
          emp.id === updatedEmployee.id
            ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
            : emp
        )
      );
    } catch (error) {
      console.error("Error inactivating QR code:", error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="employees-container">
      {editing && (
        <div className="edit-overlay">
          <div className="edit-form">
            <div className="edit-header">
              <h2>Edit Employee</h2>
              <Close
                onClick={() => setEditing(false)}
                style={{ cursor: "pointer" }}
              />
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleModify(currentEmployee);
              }}
            >
              <FormControl>
                <InputLabel htmlFor="first-name">First Name</InputLabel>
                <OutlinedInput
                  id="first-name"
                  defaultValue={currentEmployee?.first_name}
                  label="First Name"
                />
              </FormControl>
              <FormControl>
                <InputLabel htmlFor="last-name">Last Name</InputLabel>
                <OutlinedInput
                  id="last-name"
                  defaultValue={currentEmployee?.last_name}
                  label="Last Name"
                />
              </FormControl>
              <FormControl>
                <InputLabel htmlFor="email">Email</InputLabel>
                <OutlinedInput
                  id="email"
                  defaultValue={currentEmployee?.email}
                  label="Email"
                />
              </FormControl>
              <div className="button">New QR</div>
              <hr className="hr-line" />
              <button className="button button-submit" type="submit">
                Save Changes
              </button>
            </form>
            <div className="button button-cancel" onClick={() => setEditing(false)}>
              Cancel
            </div>
          </div>
        </div>
      )}
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
          <EmployeeCard
            key={emp.id}
            employee={emp}
            onDelete={handleDelete}
            onModify={showModify}
            onGenerateNewQR={handleGenerateNewQR}
            onInactivateQR={handleInactivateQR}
          />
        ))}
      </div>

      {employees.length === 0 && <p>No employees found</p>}
    </div>
  );
};

export default Employees;
