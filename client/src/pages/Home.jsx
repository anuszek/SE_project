import React, { useState } from "react";
import { Link } from "react-router-dom";
import { LockOutlined } from "@mui/icons-material";
import QRReader from "../components/QRReader";
import FaceCapture from "../components/FaceCapture";
import { verify } from "../api/verify";
import "./Home.css";

const Home = () => {
  const [step, setStep] = useState("qr"); // 'qr', 'face', 'verifying', 'result'
  const [qrData, setQrData] = useState(null);
  const [faceImage, setFaceImage] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);

  const handleQrScan = (data) => {
    if (data) {
      setQrData(data);
      setStep("face");
    }
  };

  const handleFaceCapture = (image) => {
    if (image) {
      setFaceImage(image);
      setStep("verifying");
      handleVerification(qrData, image);
    }
  };

  const handleVerification = async (qr, face) => {
    try {
      const result = await verify(qr, face);
      setVerificationResult({ success: true, data: result });
    } catch (error) {
      setVerificationResult({
        success: false,
        error: error.message || "Verification failed",
      });
    } finally {
      setStep("result");
    }
  };

  const reset = () => {
    setStep("qr");
    setQrData(null);
    setFaceImage(null);
    setVerificationResult(null);
  };

  const getStepNumber = () => {
    const steps = { qr: 1, face: 2, verifying: 3, result: 3 };
    return steps[step] || 1;
    // return 3;
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
            {currentStep > 1 ? "✓" : "1"}
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
            {currentStep > 2 ? "✓" : "2"}
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
            <p>• Look directly at the camera</p>
            <p>• Ensure good lighting conditions</p>
            <p>• Remove any face coverings or sunglasses</p>
          </div>
        );
      case "verifying":
        return (
          <div className="instructions">
            <p>
              <strong>Status:</strong>
            </p>
            <p>• Processing your credentials</p>
            <p>• Verifying identity</p>
            <p>• Please wait...</p>
          </div>
        );
      case "result":
        return (
          <div className="instructions">
            <p>
              <strong>Next Steps:</strong>
            </p>
            <p>• Review the verification result</p>
            <p>• Click the button to start a new verification</p>
            <p>• Contact support if you need assistance</p>
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
                  <QRReader onScan={handleQrScan} />
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
                <p className="step-description">
                  Position your face in the frame for identity verification
                </p>
                <div className="verification-container">
                  <FaceCapture onCapture={handleFaceCapture} />
                </div>
              </div>
              <div className="instructions-column">{renderInstructions()}</div>
            </div>
          </div>
        );
      case "verifying":
        return (
          <div className="step-card">
            <div className="step-layout">
              <div className="progress-column">{renderProgressIndicator()}</div>
              <div className="content-column">
                <p className="step-description">
                  Please wait while we verify your credentials...
                </p>

                <div className="verifying-state">
                  <div className="spinner"></div>
                  <p className="verifying-text">Processing verification...</p>
                </div>
              </div>
              <div className="instructions-column">{renderInstructions()}</div>
            </div>
          </div>
        );
      case "result":
        return (
          <div className="step-card">
            <h1 className="step-title">Verification Complete</h1>
            <div className="step-layout">
              <div className="progress-column">{renderProgressIndicator()}</div>
              <div className="content-column">
                {verificationResult?.success ? (
                  <div className="result-success">
                    <h2>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Access Granted
                    </h2>
                    <div className="result-info">
                      <p>
                        <strong>
                          Welcome, {verificationResult.data.employee.name}!
                        </strong>
                      </p>
                      <p className="timestamp">
                        Access granted at:{" "}
                        {new Date(
                          verificationResult.data.timestamp
                        ).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="result-error">
                    <h2>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Access Denied
                    </h2>
                    <div className="result-info">
                      <p>{verificationResult?.error}</p>
                    </div>
                  </div>
                )}
                <button className="action-button" onClick={reset}>
                  {verificationResult?.success
                    ? "New Verification"
                    : "Try Again"}
                </button>
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
        <Link to="/admin/dashboard" className="button">
          Admin Portal
        </Link>
      </div>
      <div className="home-content">{renderStep()}</div>
    </div>
  );
};

export default Home;
