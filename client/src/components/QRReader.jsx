import { Scanner } from "@yudiel/react-qr-scanner";
import React, { useState } from "react";
import "./QRReader.css";

const QRReader = ({ onScan, paused }) => {
  const [scannedResult, setScannedResult] = useState(null);

  return (
    <div className="qr-reader-container">
      {/* The Scanner component */}
      <Scanner
        paused={paused}
        onScan={(result) => {
          if (paused) return;
          if (result && result.length > 0) {
            const rawValue = result[0].rawValue;
            if (rawValue === scannedResult) return;
            setScannedResult(rawValue);

            if (onScan) {
              onScan(rawValue);
            }
          }
        }}
        onError={(error) => console.log(error)}
        constraints={{
          facingMode: "environment",
          width: { min: 100 }, // Ask for a very low minimum
          height: { min: 100 }, // Ask for a very low minimum
        }}
        formats={["qr_code"]}
      />
    </div>
  );
};

export default QRReader;
