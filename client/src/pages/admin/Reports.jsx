import { ArrowBack, Download, FilterList } from "@mui/icons-material";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getReports } from "../../api/admin.js";
import "./Reports.css";

const Reports = () => {
  const navigate = useNavigate();

  const [filters, setFilters] = useState({
    date_from: "",
    date_to: "",
    entry_type: "all",
    employee_id: "",
  });

  const [reportData, setReportData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultCount, setResultCount] = useState(0);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setReportData([]);

    try {
      const payload = {
        entry_type: filters.entry_type,
      };
      if (filters.date_from) payload.date_from = filters.date_from;
      if (filters.date_to) payload.date_to = filters.date_to;
      if (filters.employee_id) payload.employee_id = filters.employee_id;

      const response = await getReports(payload);

      if (response.status === "success") {
        setReportData(response.data);
        setResultCount(response.count);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reports-container">
      {/* Header */}
      <div className="reports-header">
        <div className="button" onClick={() => navigate("/admin/dashboard")}>
          <ArrowBack />
        </div>
        <h1>Reports Management</h1>
      </div>

      <div className="reports-content">
        {/* Filter Section */}
        <form className="filters-panel" onSubmit={handleGenerate}>
          <div className="filter-group">
            <label>Date From</label>
            <input
              type="date"
              name="date_from"
              value={filters.date_from}
              onChange={handleInputChange}
            />
          </div>

          <div className="filter-group">
            <label>Date To</label>
            <input
              type="date"
              name="date_to"
              value={filters.date_to}
              onChange={handleInputChange}
            />
          </div>

          <div className="filter-group">
            <label>Entry Type</label>
            <select
              name="entry_type"
              value={filters.entry_type}
              onChange={handleInputChange}
            >
              <option value="all">All Events</option>
              <option value="access">Access Granted</option>
              <option value="denied">Access Denied</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Employee ID</label>
            <input
              type="number"
              name="employee_id"
              min="1"
              placeholder="ID (optional)"
              value={filters.employee_id}
              onChange={handleInputChange}
            />
          </div>

          <button
            type="submit"
            className="generate-btn button"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Report"}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {/* Results Table */}
        <div className="results-panel">
          <div className="results-header">
            <h3>Results ({resultCount})</h3>
          </div>

          <table className="report-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Employee</th>
                <th>Status</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {reportData.length === 0 ? (
                <tr>
                  <td colSpan="4" className="empty-cell">
                    No data found
                  </td>
                </tr>
              ) : (
                reportData.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row.timestamp}</td>
                    <td>
                      <div className="emp-name">{row.full_name}</div>
                      <div className="emp-email">{row.email}</div>
                    </td>
                    <td>
                      <span className={`status-badge ${row.status}`}>
                        {row.status}
                      </span>
                    </td>
                    <td>{row.reason}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          {reportData.length > 0 && (
            <div className="button" type="button">
              <Download fontSize="small" /> &nbsp; CSV
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;
