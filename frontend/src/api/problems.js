import client from "./client";

export async function fetchProblems({ search, tag, difficulty, company, page=1, pageSize=20 }) {
  const params = {};
  if (search) params.search = search;
  if (tag) params.tag = tag;
  if (difficulty) params.difficulty = difficulty;
  if (company) params.company = company;
  params.page = page;
  params.pageSize = pageSize;

  const { data } = await client.get("/problems", { params });
  // Expect shape: { items: [...], total: N }
  return data;
}

export async function fetchCompaniesTop({ limit=20 } = {}) {
  const { data } = await client.get("/problems/companies/top", { params: { limit } });
  // Expect: [{ company: "Amazon", count: 123 }, ...]
  return data;
}
