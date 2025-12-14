import axios from 'axios';

const API_URL = '/api'; // Assuming the backend is served on the same domain

export const verify = async (qrData, faceImage) => {
  try {
    const formData = new FormData();
    formData.append('qrData', qrData);
    formData.append('faceImage', faceImage);

    const response = await axios.post(`${API_URL}/verify`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
