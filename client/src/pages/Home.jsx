import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import QRReader from "../components/QRReader";
import FaceCapture from "../components/FaceCapture";
import { verify } from "../api/verify";
import "./Home.css";

const Home = () => {
  const navigate = useNavigate();
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

  const renderStep = () => {
    switch (step) {
      case "qr":
        return (
          <div>
            <h1>Scan QR Code</h1>
            <QRReader onScan={handleQrScan} />
          </div>
        );
      case "face":
        return (
          <div>
            <h1>Face Capture</h1>
            <FaceCapture onCapture={handleFaceCapture} />
          </div>
        );
      case "verifying":
        return (
          <div>
            <h1>Verifying...</h1>
          </div>
        );
      case "result":
        return (
          <div>
            <h1>Verification Result</h1>
            {verificationResult?.success ? (
              <div>
                <h2>Welcome, {verificationResult.data.employee.name}!</h2>
                <p>
                  Access Granted at:{" "}
                  {new Date(verificationResult.data.timestamp).toLocaleString()}
                </p>
              </div>
            ) : (
              <div>
                <h2>Verification Failed</h2>
                <p>{verificationResult?.error}</p>
              </div>
            )}
            <button onClick={reset}>Try Again</button>
          </div>
        );
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <div className="button" onClick={() => navigate("/admin/dashboard")}>
          Admin Login
        </div>
      </div>
      <div className="display-area">{renderStep()}</div>
    </div>
  );
};

export default Home;
