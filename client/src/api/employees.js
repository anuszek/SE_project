import axios from "axios";

const URL = "http://localhost:5000/api/employees";

const api = axios.create({
  baseURL: URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function addEmployee(employeeData) {
  try {
    const response = await api.post("/register", employeeData);
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function modifyEmployee(employeeData) {
  try {
    const response = await api.put("/modify_employee", employeeData);
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function generateNewQrCode(employeeId) {
  try {
    const response = await api.post("/generate_new_qr_code", { employee_id: employeeId });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function inactivateQrCode(employeeId) {
  try {
    const response = await api.post("/inactive_qr_code", { employee_id: employeeId });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}
