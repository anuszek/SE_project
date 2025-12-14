import axios from "axios";

const URL = ""

const api = axios.create({
  baseURL: URL,
  headers: {
    "Content-Type": "application/json",
  },  
});

export async function addEmployee(employeeData) {
  try {
    const response = await api.post("/employees/register",employeeData);
    return response.data;
  } catch (err){
    const msg= err?.response?.data?.message || err?.message 
    throw new Error(msg)
  }
}

export async function validateEmplyee(emplyeeData) {
  try {
    const response = await api.post("/employees/verify", emplyeeData)
  //  data = request.get_json()
  //   image_input_base64 = data.get('image')
  //   qr_code = data.get('qr_code')
    return response.data
  } catch (err){
    const msg= err?.response?.data?.message || err?.message 
    throw new Error(msg)
  }
}


export async function adminClearQr() {
  try {const response = await api.post("/employee/admin/clean_qr"); // POST , GET na backend
  return response.data;
  } catch (err){
    const msg= err?.response?.data?.message || err?.message 
    throw new Error(msg)
  }
}

export async function getEmplyeeQr(employeeId) {
  try {
    const response = await api.get(`/employees/${employeeId}/qr`);
    return response.data;
  } catch (err){
    const msg= err?.response?.data?.message || err?.message 
    throw new Error(msg)
  }
}
