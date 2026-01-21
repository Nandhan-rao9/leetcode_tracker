import axios from "axios";

const client = axios.create({
  baseURL: "/api",
});

export default {
  get: async (url, config) => (await client.get(url, config)).data,
  post: async (url, body, config) => (await client.post(url, body, config)).data,
};
