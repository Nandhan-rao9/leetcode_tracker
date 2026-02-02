// src/utils/api.js
import axios from "axios";

const client = axios.create({
  baseURL: "/api",
});

const api = {
  get: async (url, config) => {
    const res = await client.get(url, config);
    return res.data;
  },
  post: async (url, body, config) => {
    const res = await client.post(url, body, config);
    return res.data;
  },
};

export default api;
