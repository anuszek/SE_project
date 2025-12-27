import { CameraAlt, CheckCircle, Refresh } from "@mui/icons-material";
import { Button } from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import "./FaceCapture.css";

const FaceCapture = ({ onCapture, automatic = false }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
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

  useEffect(() => {
    if (automatic && !isLoading && !error && stream) {
      const timer = setTimeout(() => {
        captureImage(true); // Pass a flag to indicate automatic capture
      }, 2000); // 2-second delay
      return () => clearTimeout(timer);
    }
  }, [automatic, isLoading, error, stream]);

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
      streamRef.current = mediaStream;

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
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setStream(null);
    }
  };

  const captureImage = (isAutomatic = false) => {
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

      if (isAutomatic) {
        handleConfirm(imageData);
      } else {
        setCapturedImage(imageData);
      }
    }
  };

  const handleConfirm = (image = capturedImage) => {
    if (image && onCapture) {
      stopCamera();
      onCapture(image);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    if (!stream) {
      startCamera();
    }
  };

  return (
    <div className="face-capture-container">
      <h2>Face Capture</h2>

      {error && <div className="face-capture-error">{error}</div>}

      {isLoading && !error && (
        <div className="face-capture-loading">
          <p>Loading camera...</p>
        </div>
      )}

      <div className="face-capture-video-container">
        {!capturedImage ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className={`face-capture-video ${
                isLoading || error ? "hidden" : ""
              }`}
            />
            {/* Face guide overlay */}
            <div className="face-capture-face-guide" />
          </>
        ) : (
          <img
            src={capturedImage}
            alt="Captured face"
            className="face-capture-captured-image"
          />
        )}
      </div>

      <canvas ref={canvasRef} className="face-capture-canvas" />

      <div className="face-capture-buttons">
        {!capturedImage ? (
          <Button
            variant="contained"
            color="primary"
            startIcon={<CameraAlt />}
            onClick={() => captureImage(false)}
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
              onClick={() => handleConfirm()}
              size="large"
            >
              Confirm
            </Button>
          </>
        )}
      </div>

      {!capturedImage && !error && !isLoading && (
        <div className="face-capture-info">
          <p>Position your face within the guide and click Capture</p>
        </div>
      )}
    </div>
  );
};

export default FaceCapture;
