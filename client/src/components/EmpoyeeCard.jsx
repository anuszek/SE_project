import React from "react";
import ReactDOM from "react-dom";
import QRCode from "react-qr-code";
import "./EmployeeCard.css";

const EmployeeCard = ({ employee, onDelete, onModify, onChangeQRState }) => {
  // console.log(employee);

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
      <div className="qr-code">
        {employee.is_active ? <QRCode value={employee.qr_code_data} size={150} /> : "No QR Code Active"}
      </div>
      <div className="button-group">
        <div className="button" onClick={() => onModify(employee)}>
          Edit
        </div>
        <div className="button" onClick={() => onDelete(employee)}>
          Delete
        </div>
        {employee.is_active ? (
          <div className="button" onClick={() => onChangeQRState(employee.id)}>
            Deactivate QR
          </div>
        ) : (
          <div className="button" onClick={() => onChangeQRState(employee.id)}>
            Activate QR
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeCard;
