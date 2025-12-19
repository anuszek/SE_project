import { PersonOutline } from "@mui/icons-material";
import React from "react";
import ReactDOM from "react-dom";
import QRCode from "react-qr-code";
import "./EmployeeCard.css";

const EmployeeCard = ({ employee }) => {
  return (
    <div className="employee-card">
      <div className="details">
        <h3>
          {employee.first_name} {employee.last_name}
        </h3>
        <ul>
          <li>ID: {employee.id}</li>
          <li>Email: {employee.email}</li>
          <li>Added: {new Date(employee.created_at).toLocaleDateString()}</li>
          <li>Expires: {new Date(employee.expires_at).toLocaleDateString()}</li>
        </ul>
      </div>
      <QRCode value={employee.qr_code_data} size={150} />
      <div className="button-group">
        <div className="button" onClick={ () => {}}>
          Edit
        </div>
        <div className="button" onClick={ () => {}}>
          Delete
        </div>
        <div className="button" onClick={ () => {}}>
          Deactivate QR
        </div>
        <div className="button" onClick={ () => {}}>
          Activate QR
        </div>
      </div>
    </div>
  );
};

export default EmployeeCard;
