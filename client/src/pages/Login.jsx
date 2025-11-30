import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    // Add authentication logic here
    // For now, just navigate to dashboard
    navigate("/admin/dashboard");
  };

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <h1 style={styles.title}>Admin Login</h1>
        <form onSubmit={handleLogin} style={styles.form}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button type="submit" style={styles.button}>
            Login
          </button>
        </form>
        <button onClick={() => navigate("/")} style={styles.backButton}>
          Back to Home
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    backgroundColor: "#f5f7fa",
  },
  loginBox: {
    backgroundColor: "white",
    padding: "2rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    minWidth: "350px",
  },
  title: {
    textAlign: "center",
    marginBottom: "1.5rem",
    color: "#1a202c",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  input: {
    padding: "0.75rem",
    fontSize: "1rem",
    border: "1px solid #e2e8f0",
    borderRadius: "6px",
  },
  button: {
    padding: "0.75rem",
    fontSize: "1rem",
    backgroundColor: "#667eea",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "500",
  },
  backButton: {
    marginTop: "1rem",
    padding: "0.5rem",
    fontSize: "0.9rem",
    backgroundColor: "transparent",
    color: "#718096",
    border: "1px solid #e2e8f0",
    borderRadius: "6px",
    cursor: "pointer",
    width: "100%",
  },
};

export default Login;
