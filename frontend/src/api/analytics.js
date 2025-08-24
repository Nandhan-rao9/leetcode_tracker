import client from "./client";

export async function fetchOverview({ userId }) {
  const { data } = await client.get("/analytics/overview", { params: { userId } });
  /* Suggested response:
     {
       totals: { solved: 120, last7: 10, last30: 40, streak: 5 },
       byDifficulty: { Easy: 50, Medium: 55, Hard: 15 },
       byTag: [{ tag: "Array", count: 30 }, ...],
       submissionsSeries: [{ date: "2025-08-01", count: 3 }, ...]
     }
  */
  return data;
}
