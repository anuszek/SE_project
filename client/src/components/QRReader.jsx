import React, { useState } from "react";
import { Scanner } from "@yudiel/react-qr-scanner";

const QRReader = ({ onScan }) => {
  const [scannedResult, setScannedResult] = useState(null);

  return (
    <div style={{ width: "100%", maxWidth: "400px", margin: "0 auto" }}>
      {/* The Scanner component */}
      <Scanner
        onScan={(result) => {
          if (result && result.length > 0) {
            const rawValue = result[0].rawValue;
            setScannedResult(rawValue);
            // Call the onScan callback to progress to the next step
            if (onScan) {
              onScan(rawValue);
            }
          }
        }}
        onError={(error) => console.log(error)}
        // ADD THIS PROP 👇
        constraints={{
          facingMode: "environment",
          width: { min: 100 }, // Ask for a very low minimum
          height: { min: 100 }, // Ask for a very low minimum
        }}
        formats={["qr_code"]}
      />

      {/* Display result */}
      {scannedResult && (
        <div
          style={{ marginTop: "20px", padding: "10px", background: "#f0f0f0" }}
        >
          <strong>Scanned Value:</strong> {scannedResult}
        </div>
      )}
    </div>
  );
};

export default QRReader;
