import axios from "axios";

const ADMIN_URL = "http://localhost:5000/api/admin";

const adminApi = axios.create({
  baseURL: ADMIN_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function adminClearQr() {
  try {
    const response = await adminApi.post("/clean_qr"); // POST , GET na backend
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function getAccessLogs(limit = 15) {
  try {
    const response = await adminApi.get(`/logs?limit=${limit}`);
    return response.data.logs;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function getEmployeeStats() {
  try {
    const response = await adminApi.get("/stats");
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}
