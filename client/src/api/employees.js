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

export async function getEmployeeQr(employeeId) {
  try {
    const response = await api.get(`/${employeeId}/qr`);
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}
