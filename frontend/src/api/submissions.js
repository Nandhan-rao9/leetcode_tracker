import client from "./client";

export async function fetchSubmissions({ userId, from, to, page=1, pageSize=50 }) {
  const params = { userId, page, pageSize };
  if (from) params.from = from;
  if (to) params.to = to;
  const { data } = await client.get("/submissions", { params });
  // Expect shape: { items: [...], total: N }
  return data;
}
