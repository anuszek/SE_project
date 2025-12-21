import axios from "axios";

const URL = "http://localhost:5000/api/employees";

const api = axios.create({
  baseURL: URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function fetchEmployees() {
  try {
    const response = await api.get("/all");
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function addEmployee(employeeData) {
  try {
    const response = await api.post("/register", employeeData);
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function deleteEmployee(employeeId) {
  try {
    const response = await api.delete(`/${employeeId}/delete`, {
      data: { employee_id: employeeId },
    });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function modifyEmployee(employeeData) {
  try {
    const response = await api.put(`/${employeeData.id}/modify_employee`, employeeData);
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function generateNewQR(employeeId) {
  try {
    const response = await api.post(`/${employeeId}/generate_new_qr_code`, {
      employee_id: employeeId,
    });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}

export async function changeQRState(employeeId, isActive) {
  try {
    const response = await api.post(`/${employeeId}/switch_qr_state`, {
      is_active: isActive
    });
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
}
