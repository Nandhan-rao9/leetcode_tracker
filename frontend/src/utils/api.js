// src/utils/api.js
import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000",
  timeout: 8000,
});

// simple wrapper - returns data or throws
export default {
  get: async (path, params = {}) => {
    const res = await API.get(path, { params });
    return res.data;
  },
  post: async (path, body = {}) => {
    const res = await API.post(path, body);
    return res.data;
  }
};
