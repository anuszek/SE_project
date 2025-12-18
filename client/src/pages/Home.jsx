import {
  CheckCircleOutlined,
  CheckOutlined,
  DoDisturbOnOutlined,
  LockOutlined,
} from "@mui/icons-material";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { verifyFace, verifyQRCode } from "../api/auth";
import FaceCapture from "../components/FaceCapture";
import QRReader from "../components/QRReader";
import "./Home.css";

const Home = () => {
  const [step, setStep] = useState("qr"); // 'qr', 'face', 'verifying-background', 'result'
  const [isPaused, setIsPaused] = useState(false);
  const [qrData, setQrData] = useState(null);
  const [employeeId, setEmployeeId] = useState(null);
  const [faceImage, setFaceImage] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [accessGranted, setAccessGranted] = useState(false);

  const handleQrScan = async (data) => {
    if (isPaused) return;

    setIsPaused(true);
    console.log("Processing:", data);

    try {
      const result = await verifyQRCode(data);
      setQrData(data);
      setEmployeeId(result.employee_id);
      setAccessGranted(true);
      setStep("face");
    } catch (error) {
      console.error("Verification failed:", error);

      setTimeout(() => {
        setIsPaused(false);
      }, 2000);
    }
  };

  const handleFaceCapture = (image) => {
    if (image) {
      setFaceImage(image);
      setStep("verifying-background");
      handleVerification(employeeId, image);
    }
  };

  const handleVerification = async (empId, face) => {
    try {
      const result = await verifyFace(empId, face);
      // You can use this result for logging or minor UI feedback
      setVerificationResult({ success: true, data: result });
      console.log("Background verification success:", result);
      setTimeout(() => reset(), 2000);
    } catch (error) {
      setVerificationResult({
        success: false,
        error: error.message || "Verification failed",
      });
      console.error("Background verification error:", error);
      setTimeout(() => reset(), 3000);
    }
  };

  const reset = () => {
    setStep("qr");
    setQrData(null);
    setFaceImage(null);
    setVerificationResult(null);
    setAccessGranted(false);
  };

  const getStepNumber = () => {
    const steps = { qr: 1, face: 2, "verifying-background": 3, result: 3 };
    return steps[step] || 1;
  };

  const renderProgressIndicator = () => {
    const currentStep = getStepNumber();

    return (
      <div className="progress-indicator">
        <div className="progress-step">
          <div
            className={`progress-step-circle ${
              currentStep >= 1 ? "active" : ""
            } ${currentStep > 1 ? "completed" : ""}`}
          >
            {currentStep > 1 ? <CheckOutlined /> : "1"}
          </div>
          <span
            className={`progress-step-label ${
              currentStep === 1 ? "active" : ""
            } ${currentStep > 1 ? "completed" : ""}`}
          >
            Scan QR
          </span>
        </div>

        <div
          className={`progress-connector ${currentStep > 1 ? "completed" : ""}`}
        ></div>

        <div className="progress-step">
          <div
            className={`progress-step-circle ${
              currentStep >= 2 ? "active" : ""
            } ${currentStep > 2 ? "completed" : ""}`}
          >
            {currentStep > 2 ? <CheckOutlined /> : "2"}
          </div>
          <span
            className={`progress-step-label ${
              currentStep === 2 ? "active" : ""
            } ${currentStep > 2 ? "completed" : ""}`}
          >
            Face Scan
          </span>
        </div>

        <div
          className={`progress-connector ${currentStep > 2 ? "completed" : ""}`}
        ></div>

        <div className="progress-step">
          <div
            className={`progress-step-circle ${
              currentStep >= 3 ? "active" : ""
            }`}
          >
            3
          </div>
          <span
            className={`progress-step-label ${
              currentStep === 3 ? "active" : ""
            }`}
          >
            Verify
          </span>
        </div>
      </div>
    );
  };

  const renderInstructions = () => {
    switch (step) {
      case "qr":
        return (
          <div className="instructions">
            <p>
              <strong>Instructions:</strong>
            </p>
            <p>• Position your QR code in front of the camera</p>
            <p>• Make sure the code is clearly visible</p>
            <p>• Hold steady until the scan is complete</p>
          </div>
        );
      case "face":
        return (
          <div className="instructions">
            <p>
              <strong>Instructions:</strong>
            </p>
            <p>• Look directly at the camera for a quick photo</p>
            <p>• This is for identity verification purposes</p>
            <p>• The capture is automatic</p>
          </div>
        );
      case "verifying-background":
        return (
          <div className="instructions">
            <p>
              <strong>Status:</strong>
            </p>
            <p>• Verification is processing in the background</p>
            <p>• Thank you!</p>
          </div>
        );
      default:
        return null;
    }
  };

  const renderStep = () => {
    switch (step) {
      case "qr":
        return (
          <div className="step-card">
            <div className="step-layout">
              <div className="progress-column">{renderProgressIndicator()}</div>
              <div className="content-column">
                <div className="verification-container">
                  <QRReader onScan={handleQrScan} paused={isPaused} />
                </div>
                <p className="step-description">
                  Scan your QR code to begin the verification process
                </p>
              </div>
              <div className="instructions-column">{renderInstructions()}</div>
            </div>
          </div>
        );
      case "face":
        return (
          <div className="step-card">
            <div className="step-layout">
              <div className="progress-column">{renderProgressIndicator()}</div>
              <div className="content-column">
                {accessGranted && (
                  <div
                    className="result-success"
                    style={{ marginBottom: "20px" }}
                  >
                    <h2>
                      <CheckCircleOutlined />
                      Access Granted
                    </h2>
                  </div>
                )}
                <p className="step-description">
                  Please look at the camera for identity verification.
                </p>
                <div className="verification-container">
                  <FaceCapture onCapture={handleFaceCapture} automatic={true} />
                </div>
              </div>
              <div className="instructions-column">{renderInstructions()}</div>
            </div>
          </div>
        );
      case "verifying-background":
        return (
          <div className="step-card">
            <div className="step-layout">
              <div className="progress-column">{renderProgressIndicator()}</div>
              <div className="content-column">
                <div className="result-success">
                  <h2>
                    <CheckCircleOutlined /> Thank You!
                  </h2>
                  <p className="step-description">
                    Your verification is being processed.
                  </p>
                </div>
              </div>
              <div className="instructions-column">{renderInstructions()}</div>
            </div>
          </div>
        );
      default:
        return (
          <div className="step-card">
            <h1>Unknown step</h1>
          </div>
        );
    }
  };

  return (
    <div className="home-container">
      <div className="home-header">
        <div className="home-logo">
          <LockOutlined />
          Access Control System
        </div>
        <Link to="/login" className="button">
          Admin Portal
        </Link>
      </div>
      <div className="home-content">{renderStep()}</div>
    </div>
  );
};

export default Home;
