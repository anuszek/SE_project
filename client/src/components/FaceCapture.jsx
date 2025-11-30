import React, { useRef, useState, useEffect } from "react";
import { Button } from "@mui/material";
import { CameraAlt, CheckCircle, Refresh } from "@mui/icons-material";

const FaceCapture = ({ onCapture }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsLoading(false);
    } catch (err) {
      console.error("Error accessing camera:", err);
      setError(
        "Unable to access camera. Please ensure you have granted camera permissions."
      );
      setIsLoading(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw the video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to base64 image
      const imageData = canvas.toDataURL("image/jpeg", 0.8);
      setCapturedImage(imageData);
    }
  };

  const handleConfirm = () => {
    if (capturedImage && onCapture) {
      stopCamera();
      onCapture(capturedImage);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    if (!stream) {
      startCamera();
    }
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "500px",
        margin: "0 auto",
        textAlign: "center",
      }}
    >
      <h2>Face Capture</h2>

      {error && (
        <div
          style={{
            padding: "15px",
            marginBottom: "20px",
            background: "#ffebee",
            color: "#c62828",
            borderRadius: "8px",
          }}
        >
          {error}
        </div>
      )}

      {isLoading && !error && (
        <div style={{ padding: "20px" }}>
          <p>Loading camera...</p>
        </div>
      )}

      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "640px",
          margin: "0 auto",
          borderRadius: "12px",
          overflow: "hidden",
          background: "#000",
        }}
      >
        {!capturedImage ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{
                width: "100%",
                height: "auto",
                display: isLoading || error ? "none" : "block",
              }}
            />
            {/* Face guide overlay */}
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: "200px",
                height: "250px",
                border: "3px solid rgba(76, 175, 80, 0.6)",
                borderRadius: "50%",
                pointerEvents: "none",
              }}
            />
          </>
        ) : (
          <img
            src={capturedImage}
            alt="Captured face"
            style={{ width: "100%", height: "auto" }}
          />
        )}
      </div>

      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div
        style={{
          marginTop: "20px",
          display: "flex",
          gap: "10px",
          justifyContent: "center",
        }}
      >
        {!capturedImage ? (
          <Button
            variant="contained"
            color="primary"
            startIcon={<CameraAlt />}
            onClick={captureImage}
            disabled={isLoading || error}
            size="large"
          >
            Capture
          </Button>
        ) : (
          <>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRetake}
              size="large"
            >
              Retake
            </Button>
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckCircle />}
              onClick={handleConfirm}
              size="large"
            >
              Confirm
            </Button>
          </>
        )}
      </div>

      {!capturedImage && !error && !isLoading && (
        <div
          style={{
            marginTop: "20px",
            padding: "10px",
            background: "#e3f2fd",
            borderRadius: "8px",
          }}
        >
          <p style={{ margin: 0, fontSize: "14px", color: "#1565c0" }}>
            Position your face within the guide and click Capture
          </p>
        </div>
      )}
    </div>
  );
};

export default FaceCapture;
