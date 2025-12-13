import React, { useState } from "react";
import QRCode from "react-qr-code";
import { useNavigate } from "react-router-dom";
import "./Employees.css";

const Employees = () => {
  const navigate = useNavigate();
  const [qrValue, setQrValue] = useState("EmployeeID-12345");

  return (
    <div className="employees-container">
      <QRCode value={ qrValue } />
    </div>
  );
};

export default Employees;
