import { useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";
import { fetchSubmissions } from "../api/submissions";
import { fetchProblems } from "../api/problems";
import Filters from "../components/Filters";
import ProblemRow from "../components/ProblemRow";

const DUE_DAYS = 14;

export default function Revision() {
  const userId = process.env.REACT_APP_DEFAULT_USER_ID || "harshan";
  const [subs, setSubs] = useState({ items: [], total: 0 });
  const [filters, setFilters] = useState({});
  const [problemsMap, setProblemsMap] = useState(new Map()); // slug/url -> problem meta (difficulty, tags, numOccur)
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async ()=> {
      setLoading(true);
      try {
        const s = await fetchSubmissions({ userId, pageSize: 500 }); // pull a chunk
        setSubs(s);

        // Optional: enrich problems (best via backend). For now, a small pass:
        const p = await fetchProblems({ pageSize: 1 }); // ping to ensure API healthy
        // In v1, we’ll rely on the submission payload having: slug/title/url/difficulty/tags if your backend already joins them.
      } finally {
        setLoading(false);
      }
    })();
  }, [userId]);

  const uniqueByProblem = useMemo(() => {
    const latest = new Map();
    for (const it of (subs.items || [])) {
      // Expect each submission item to include: problemId or slug/url, title, url, difficulty, lcTags, submittedAt
      const key = it.problemId || it.slug || it.url || it.title;
      const ts = +new Date(it.submittedAt);
      const prev = latest.get(key);
      if (!prev || ts > +new Date(prev.submittedAt)) {
        latest.set(key, it);
      }
    }
    return Array.from(latest.values());
  }, [subs]);

  const dueList = useMemo(() => {
    const now = dayjs();
    let list = uniqueByProblem
      .map((it) => {
        const lastDate = dayjs(it.submittedAt);
        const daysAgo = now.diff(lastDate, "day");
        return {
          ...it,
          lastSolvedAt: it.submittedAt,
          _due: daysAgo >= DUE_DAYS,
          _daysAgo: daysAgo,
        };
      })
      .filter((it) => it._due);

    // client-side filters
    if (filters.search) {
      const q = filters.search.toLowerCase();
      list = list.filter((x) => (x.title || "").toLowerCase().includes(q));
    }
    if (filters.difficulty) {
      list = list.filter((x) => (x.difficulty || "") === filters.difficulty);
    }
    if (filters.tag) {
      const t = filters.tag.toLowerCase();
      list = list.filter((x) => (x.lcTags || []).some((k) => (k || "").toLowerCase().includes(t)));
    }

    // sort by oldest (most due) first
    list.sort((a, b) => +new Date(a.lastSolvedAt) - +new Date(b.lastSolvedAt));
    return list;
  }, [uniqueByProblem, filters]);

  return (
    <div>
      <h2>Revision</h2>
      <p className="subtle">Shows problems last solved ≥ {DUE_DAYS} days ago.</p>
      <Filters onChange={setFilters} initial={{}} />
      {loading && <div>Loading…</div>}

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Problem</th>
              <th>Difficulty</th>
              <th>Tags</th>
              <th style={{textAlign:"right"}}>Company Freq</th>
              <th>Last Solved</th>
            </tr>
          </thead>
          <tbody>
            {dueList.map((item) => (
              <ProblemRow key={(item.problemId || item.slug || item.url || item.title)} item={item} />
            ))}
          </tbody>
        </table>
        {!loading && dueList.length === 0 && <div className="empty">Nothing due yet 🎉</div>}
      </div>
    </div>
  );
}
