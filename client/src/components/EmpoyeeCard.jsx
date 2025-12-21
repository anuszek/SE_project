import React from "react";
import ReactDOM from "react-dom";
import QRCode from "react-qr-code";
import "./EmployeeCard.css";

const EmployeeCard = ({
  employee,
  onDelete,
  onModify,
  onGenerateNewQR,
  onInactivateQR,
}) => {
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
        <QRCode value={employee.qr_code} size={150} />
      </div>
      <div className="button-group">
        <div className="button" onClick={() => onModify(employee)}>
          Edit
        </div>
        <div className="button" onClick={() => onDelete(employee.id)}>
          Delete
        </div>
        {employee.is_active ? (
          <div className="button" onClick={() => onInactivateQR(employee.id)}>
            Deactivate
          </div>
        ) : (
          <div className="button" onClick={() => onGenerateNewQR(employee.id)}>
            Activate
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeCard;
