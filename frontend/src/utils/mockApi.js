// Simulates API responses until backend is ready
export const mockFetch = (path, delay = 400) =>
  new Promise((res) =>
    setTimeout(() => {
      if (path === "/api/summary")
        return res({ totalSolved: 253, totalProblems: 1263, companies: 187 });
      if (path === "/api/companies/top")
        return res([
          { name: "Amazon", count: 412, ready: 0.82 },
          { name: "Google", count: 348, ready: 0.54 },
          { name: "Meta", count: 295, ready: 0.33 },
          { name: "Microsoft", count: 210, ready: 0.47 },
        ]);
      if (path.startsWith("/api/companies/"))
        return res({
          problems: Array.from({ length: 8 }, (_, i) => ({
            id: `${path}-p-${i}`,
            title: `Sample Problem ${i + 1}`,
            difficulty: ["Easy", "Medium", "Hard"][i % 3],
            topics: ["Arrays", "DP", "Graphs"].slice(0, (i % 3) + 1),
            num_occur: (i + 1) * 23,
          })),
        });
      return res({});
    }, delay)
  );
