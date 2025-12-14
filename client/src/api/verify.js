import axios from "axios";

const URL = "http://localhost:5000/api/employees";

const api = axios.create({
  baseURL: URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function verifyEmployee(qrCode){
  try {
    const response = await api.post("/verify", { qrCode });
    console.log("responseee" + response);
    
    return response.data;
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message;
    throw new Error(msg);
  }
};





