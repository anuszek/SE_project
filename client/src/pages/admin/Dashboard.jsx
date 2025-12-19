import {
  AccountCircleOutlined,
  AssessmentOutlined,
  BrowseGalleryOutlined,
  CheckCircleOutlineOutlined,
  ChecklistRtlOutlined,
  ManageAccountsOutlined,
  PeopleOutline,
  PersonAddAltOutlined,
  QrCodeOutlined,
  SyncOutlined,
  LocalPolice,
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
        pendingVerifications: statsData.pending_verifications,
      };

      setStats(newStats);

      const logsData = await getAccessLogs(newStats.todayAccess);

      setRecentActivity(
        logsData.map((log) => ({
          id: log.id,
          employee: log.employee_name || `Employee ${log.employee_id}`,
          action: log.status === "granted" ? "Checked In" : "Denied",
          method:
            log.verification_method === "face" ? "Face Recognition" : "QR Code",
          time: new Date(log.timestamp).toLocaleTimeString(),
        }))
      );

      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
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
          <Link to="/admin/settings" className="button">
            Settings
          </Link>
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
            <h3>{stats.pendingVerifications}</h3>
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
          <Link to="/admin/reports" className="view-all-link">
            View All
          </Link>
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
    </div>
  );
};

export default Dashboard;
