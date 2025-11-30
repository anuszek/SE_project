import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  PeopleOutline,
  CheckCircleOutlineOutlined,
  ChecklistRtlOutlined,
  BrowseGalleryOutlined,
  SyncOutlined,
  PersonAddAltOutlined,
  ManageAccountsOutlined,
  AssessmentOutlined,
  AccountCircleOutlined,
  QrCodeOutlined,
} from "@mui/icons-material";
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
      // Mock data - replace with actual API calls
      setStats({
        totalEmployees: 125,
        activeEmployees: 118,
        todayAccess: 87,
        pendingVerifications: 5,
      });

      setRecentActivity([
        {
          id: 1,
          employee: "John Doe",
          action: "Checked In",
          time: "10:30 AM",
          method: "Face Recognition",
        },
        {
          id: 2,
          employee: "Jane Smith",
          action: "Checked Out",
          time: "10:15 AM",
          method: "QR Code",
        },
        {
          id: 3,
          employee: "Mike Johnson",
          action: "Checked In",
          time: "9:45 AM",
          method: "Face Recognition",
        },
        {
          id: 4,
          employee: "Sarah Williams",
          action: "Checked In",
          time: "9:30 AM",
          method: "QR Code",
        },
        {
          id: 5,
          employee: "Tom Brown",
          action: "Checked Out",
          time: "9:15 AM",
          method: "Face Recognition",
        },
      ]);

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
        <div>
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
            <BrowseGalleryOutlined />
          </div>
          <div className="stat-content">
            <h3>{stats.pendingVerifications}</h3>
            <p>Pending Verifications</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/admin/employees" className="action-button action-primary">
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
