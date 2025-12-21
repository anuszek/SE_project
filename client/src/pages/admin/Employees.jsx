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
  changeQRState,
  deleteEmployee,
  fetchEmployees,
  generateNewQR,
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
  const [confirmation, setConfirmation] = useState(false);

  useEffect(() => {
    getEmployees();
  }, []);

  const getEmployees = async () => {
    try {
      const data = await fetchEmployees();

      setEmployees(
        data.map((emp) => ({
          ...emp,
        }))
      );
    } catch (error) {
      console.error("Error fetching employees:", error);
    } finally {
      setLoading(false);
    }
  };

  const showDeleteConfirmation = (employeeData) => {
    setConfirmation(true);
    setCurrentEmployee(employeeData);
  };

  const handleDelete = async (employeeId) => {
    try {
      await deleteEmployee(employeeId);
      setEmployees(employees.filter((emp) => emp.id !== employeeId));
    } catch (error) {
      console.error("Error deleting employee:", error);
    } finally {
      setConfirmation(false);
    }
  };

  const showModify = (employeeData) => {
    setEditing(true);
    setCurrentEmployee(employeeData);
  };

  const handleModify = async (employeeData) => {
    const newData = {
      id: employeeData.id,
      first_name: document.getElementById("first-name").value,
      last_name: document.getElementById("last-name").value,
      email: document.getElementById("email").value,
    };

    try {
      const updatedEmployee = await modifyEmployee(newData);
      setEmployees(
        employees.map((emp) =>
          emp.id === updatedEmployee.id
            ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
            : emp
        )
      );
      getEmployees();
      setEditing(false);
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

      const button = document.getElementById("new_qr");
      button.innerHTML = "<p>QR Generated, save to apply</p>";
      button.removeAttribute("class")
    } catch (error) {
      console.error("Error generating new QR code:", error);
    }
  };

  const handleQRState = async (employeeData) => {
    const employeeId = employeeData.id;
    console.log(employeeData);
    if (!employeeData.qr_credential.is_active) {
      try {
        const updatedEmployee = await changeQRState(employeeId, true);
        setEmployees(
          employees.map((emp) =>
            emp.id === updatedEmployee.id
              ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
              : emp
          )
        );
        getEmployees();
      } catch (error) {
        console.error("Error activating QR code:", error);
      }
    } else {
      try {
        const updatedEmployee = await changeQRState(employeeId, false);
        setEmployees(
          employees.map((emp) =>
            emp.id === updatedEmployee.id
              ? { ...updatedEmployee, qr_code_data: updatedEmployee.qr_code }
              : emp
          )
        );
        getEmployees();
      } catch (error) {
        console.error("Error inactivating QR code:", error);
      }
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="employees-container">
      {editing && (
        <div className="overlay">
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
              <div
                id="new_qr"
                className="button"
                onClick={() => handleGenerateNewQR(currentEmployee.id)}
              >
                New QR
              </div>
              <hr className="hr-line" />
              <button className="button button-submit" type="submit">
                Save Changes
              </button>
            </form>
            <div
              className="button button-cancel"
              onClick={() => setEditing(false)}
            >
              Cancel
            </div>
          </div>
        </div>
      )}
      {confirmation && (
        <div className="overlay">
          <div className="confirmation-box">
            <p>Are you sure you want to delete this employee?</p>
            <div className="confirmation-buttons">
              <div
                className="button button-submit"
                onClick={() => handleDelete(currentEmployee.id)}
              >
                Yes
              </div>
              <div
                className="button button-cancel"
                onClick={() => {
                  setConfirmation(false);
                }}
              >
                No
              </div>
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
            Delete, modify or generate new QR codes for your employees
          </p>
        </div>
      </div>

      <div className="employees-list">
        {employees.map((emp) => (
          <EmployeeCard
            key={emp.id}
            employee={emp}
            onDelete={showDeleteConfirmation}
            onModify={showModify}
            onChangeQRState={handleQRState}
          />
        ))}
      </div>

      {employees.length === 0 && <p>No employees found</p>}
    </div>
  );
};

export default Employees;
