import {
  AccountCircleOutlined,
  AssessmentOutlined,
  CheckCircleOutlineOutlined,
  ChecklistRtlOutlined,
  Close, 
  LocalPolice,
  ManageAccountsOutlined,
  PeopleOutline,
  PersonAddAltOutlined,
  QrCodeOutlined,
  SyncOutlined,
} from "@mui/icons-material";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAccessLogs, getEmployeeStats } from "../../api/admin";
import "./Dashboard.css";

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    activeEmployees: 0,
    todayAccess: 0,
    pendingVerifications: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [allLogs, setAllLogs] = useState([]);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const statsData = await getEmployeeStats();

      const newStats = {
        totalEmployees: statsData.total_employees,
        activeEmployees: statsData.active_employees,
        todayAccess: statsData.today_access,
        incorrectEntries: statsData.today_denied,
      };

      setStats(newStats);

      // Fetch limited logs for the dashboard widget
      const logsData = await getAccessLogs(newStats.todayAccess);
      setRecentActivity(formatLogs(logsData));

      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
    }
  };

  // Helper to format logs consistently for both dashboard and modal
  const formatLogs = (data) => {
    return data.map((log) => ({
      id: log.id,
      employee: log.employee_name || `Employee ${log.employee_id}`,
      action: log.status === "granted" ? "Checked In" : "Denied",
      method:
        log.verification_method === "face" ? "Face Recognition" : "QR Code",
      time: new Date(log.timestamp).toLocaleString(), // Changed to toLocaleString for full date in modal
    }));
  };

  const handleViewAllClick = async () => {
    setShowModal(true);
    setModalLoading(true);
    try {
      // Assuming getAccessLogs without arguments or with a specific flag returns all history
      // You might need to adjust this API call based on your backend pagination logic
      const allData = await getAccessLogs();
      setAllLogs(formatLogs(allData));
    } catch (error) {
      console.error("Error fetching all logs", error);
    } finally {
      setModalLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p className="dashboard-subtitle">
            Welcome back! Here's your overview
          </p>
        </div>
        <div className="header-actions">
          <Link to="/" className="button">
            Back to Home
          </Link>
          <div className="button">Settings</div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card stat-card-primary">
          <div className="stat-icon">
            <PeopleOutline />
          </div>
          <div className="stat-content">
            <h3>{stats.totalEmployees}</h3>
            <p>Total Employees</p>
          </div>
        </div>

        <div className="stat-card stat-card-success">
          <div className="stat-icon">
            <CheckCircleOutlineOutlined />
          </div>
          <div className="stat-content">
            <h3>{stats.activeEmployees}</h3>
            <p>Active Employees</p>
          </div>
        </div>

        <div className="stat-card stat-card-info">
          <div className="stat-icon">
            <ChecklistRtlOutlined />
          </div>
          <div className="stat-content">
            <h3>{stats.todayAccess}</h3>
            <p>Today's Access Logs</p>
          </div>
        </div>

        <div className="stat-card stat-card-warning">
          <div className="stat-icon">
            <LocalPolice />
          </div>
          <div className="stat-content">
            <h3>{stats.incorrectEntries}</h3>
            <p>Incorrect Entries</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link
            to="/admin/add-employee"
            className="action-button action-primary"
          >
            <PersonAddAltOutlined />
            <span>Add Employee</span>
          </Link>

          <Link
            to="/admin/employees"
            className="action-button action-secondary"
          >
            <ManageAccountsOutlined />
            <span>Manage Employees</span>
          </Link>

          <Link to="/admin/reports" className="action-button action-info">
            <AssessmentOutlined />
            <span>View Reports</span>
          </Link>

          <div
            className="action-button action-success"
            onClick={fetchDashboardData}
          >
            <SyncOutlined />
            <span>Refresh Data</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <div className="activity-header">
          <h2>Recent Activity</h2>
          {/* Changed Link to a button/span with onClick */}
          <span
            className="view-all-link"
            onClick={handleViewAllClick}
            style={{ cursor: "pointer" }}
          >
            View All
          </span>
        </div>
        <div className="activity-table">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Action</th>
                <th>Method</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {recentActivity.map((activity) => (
                <tr key={activity.id}>
                  <td className="employee-name">{activity.employee}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        activity.action === "Checked In"
                          ? "status-in"
                          : "status-out"
                      }`}
                    >
                      {activity.action}
                    </span>
                  </td>
                  <td className="method-cell">
                    {activity.method === "Face Recognition" ? (
                      <span className="method-tag method-face">
                        <AccountCircleOutlined />
                        Face
                      </span>
                    ) : (
                      <span className="method-tag method-qr">
                        <QrCodeOutlined />
                        QR Code
                      </span>
                    )}
                  </td>
                  <td className="time-cell">{activity.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Full History Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <h2>All Access Logs</h2>
              <button
                className="close-button"
                onClick={() => setShowModal(false)}
              >
                <Close />
              </button>
            </div>

            <div className="modal-body">
              {modalLoading ? (
                <div className="loading-spinner">Loading history...</div>
              ) : (
                <div className="activity-table full-width-table">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Employee</th>
                        <th>Action</th>
                        <th>Method</th>
                        <th>Date & Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {allLogs.map((activity) => (
                        <tr key={activity.id}>
                          <td>#{activity.id}</td>
                          <td className="employee-name">{activity.employee}</td>
                          <td>
                            <span
                              className={`status-badge ${
                                activity.action === "Checked In"
                                  ? "status-in"
                                  : "status-out"
                              }`}
                            >
                              {activity.action}
                            </span>
                          </td>
                          <td className="method-cell">
                            {activity.method === "Face Recognition" ? (
                              <span className="method-tag method-face">
                                <AccountCircleOutlined />
                                Face
                              </span>
                            ) : (
                              <span className="method-tag method-qr">
                                <QrCodeOutlined />
                                QR Code
                              </span>
                            )}
                          </td>
                          <td className="time-cell">{activity.time}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
