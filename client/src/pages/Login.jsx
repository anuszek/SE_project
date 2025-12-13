import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const handleLogin = () => {
    // Add authentication logic here
    // For now, just navigate to dashboard
    navigate("/admin/dashboard");
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">Administrator Login</h1>

        {loginError && (
          <div className="login-error">
            <span>!!!</span> {loginError}
          </div>
        )}

        <div className="login-form">
          <div className="input-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="login-input"
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="login-input"
            />
          </div>

          <div className="button" onClick={handleLogin}>
            Log In
          </div>

          <hr className="hr-line"/>

          <Link to="/" className="button">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
