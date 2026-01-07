import axios from "axios";

const API_BASE = "http://localhost:8000"; // FastAPI backend


export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file); // MUST be "file"

  return axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};


export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${API_BASE}/upload`, formData);
};

export const uploadDocuments = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  return axios.post(`${API_BASE}/upload-multiple`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const askQuestion = async (question) => {
  return axios.post(
    `${API_BASE}/ask`,
    { question }, // JSON body
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
};


export const clearChat = async () => {
  return axios.post(`${API_BASE}/clear-chat`);
};

export const resetKnowledge = async () => {
  return axios.post(`${API_BASE}/reset`);
};
