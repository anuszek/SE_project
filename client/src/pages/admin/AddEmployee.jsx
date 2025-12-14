import { ArrowBack, Close, CloudUpload, PersonAdd } from "@mui/icons-material";
import { CircularProgress, TextField } from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { addEmployee } from "../../api/employees";
import "./AddEmployee.css";

const AddEmployee = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
  });
  const [uploadedImage, setUploadedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => {
        setErrorMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = "First name is required";
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = "Last name is required";
    }
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email";
    }
    if (!uploadedImage) {
      newErrors.image = "Photo is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!validTypes.includes(file.type)) {
      setErrors((prev) => ({
        ...prev,
        image: "Please upload a valid image file (JPG, PNG)",
      }));
      return;
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setErrors((prev) => ({
        ...prev,
        image: "File size must be less than 5MB",
      }));
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result;
      setUploadedImage(base64);
      if (errors.image) {
        setErrors((prev) => ({
          ...prev,
          image: "",
        }));
      }
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setUploadedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const employeeData = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim(),
        image: uploadedImage,
      };

      const response = await addEmployee(employeeData);
      setSuccessMessage("Employee added successfully!");

      setTimeout(() => {
        navigate("/admin/employees");
      }, 2000);
    } catch (error) {
      setErrorMessage(
        error.response?.data?.message ||
          "Error adding employee. Please try again."
      );
      console.error("Error adding employee:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-employee-container">
      {/* Error Toast */}
      {errorMessage && (
        <div className="message-container error-message">
          <span>!</span> {errorMessage}
          <button
            type="button"
            className="error-close-btn"
            onClick={() => setErrorMessage("")}
            aria-label="Close error message"
          >
            <Close fontSize="small" />
          </button>
        </div>
      )}

      {/* Header */}
      <div className="add-employee-header">
        <div className="button" onClick={() => navigate("/admin/dashboard")}>
          <ArrowBack />
        </div>
        <div>
          <h1>Add New Employee</h1>
          <p className="subtitle">
            Fill in the employee information and capture their face
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="add-employee-content">
        <form onSubmit={handleSubmit} className="add-employee-form">
          {/* Left Column - Form Fields */}
          <div className="form-section">
            <div className="form-card">
              <h2 className="section-title">
                <PersonAdd /> Employee Information
              </h2>

              <div className="form-group">
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  error={!!errors.first_name}
                  helperText={errors.first_name}
                  placeholder=""
                  variant="outlined"
                />
              </div>

              <div className="form-group">
                <TextField
                  fullWidth
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  error={!!errors.last_name}
                  helperText={errors.last_name}
                  placeholder=""
                  variant="outlined"
                />
              </div>

              <div className="form-group">
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  error={!!errors.email}
                  helperText={errors.email}
                  placeholder=""
                  variant="outlined"
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="form-actions">
              <div
                type="button"
                className="button"
                onClick={() => navigate("/admin/employees")}
                disabled={loading}
              >
                Cancel
              </div>
              <button
                type="submit"
                className="button"
              >
                  Add Employee
              </button>
            </div>
          </div>
          <div className="face-section">
            <div className="form-card face-card">
              <h2 className="section-title">
                <CloudUpload /> Upload Photo
              </h2>

              <div className="face-preview-container">
                {uploadedImage ? (
                  <>
                    <img
                      src={uploadedImage}
                      alt="Uploaded photo"
                      className="captured-image"
                    />
                    <p className="success-text">Photo uploaded successfully</p>
                    <div className="button-group">
                      <div
                        type="button"
                        className="button"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        Change Photo
                      </div>
                      <div
                        type="button"
                        className="button"
                        onClick={handleRemoveImage}
                      >
                        Remove
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="empty-state">
                      <CloudUpload className="empty-icon" />
                      <p>No photo uploaded yet</p>
                    </div>
                    <div
                      type="button"
                      className="button"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Upload Photo
                    </div>
                  </>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  style={{ display: "none" }}
                />
                {errors.image && <p className="error-text">{errors.image}</p>}
              </div>
            </div>
          </div>
        </form>

        {/* Messages */}
        {successMessage && (
          <div className="message-container success-message">
            <span>✓</span> {successMessage}
          </div>
        )}
      </div>
    </div>
  );
};

export default AddEmployee;
