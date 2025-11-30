import React from "react";
import { Scanner } from "@yudiel/react-qr-scanner";

const QRReader = ({ onScan }) => {
  const handleScan = (detectedCodes) => {
    console.log("Detected codes:", detectedCodes);
    // detectedCodes is an array of IDetectedBarcode objects
    detectedCodes.forEach((code) => {
      console.log(`Format: ${code.format}, Value: ${code.rawValue}`);
    });
  };

  return (
    <Scanner
      onScan={handleScan}
      onError={(error) => console.error(error)}
      components={{
        audio: true,
      }}
    />
  );
};

export default QRReader;
