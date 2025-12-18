import axios from "axios";

const URL = "http://localhost:5000/api/auth";

const api = axios.create({
  baseURL: URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function verifyQRCode(qrCode) {
  try {
    const response = await api.post("/qr", { qr_code: qrCode });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function verifyFace(employeeId, image) {
  try {
    const response = await api.post("/face", {
      employee_id: employeeId,
      image: image,
    });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}