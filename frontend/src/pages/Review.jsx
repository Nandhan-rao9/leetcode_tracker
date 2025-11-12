import React, { useEffect, useState } from "react";
import api from "../utils/api";

export default function Review() {
  const [problems, setProblems] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/api/review/today");
        setProblems(res);
      } catch {
        setProblems([]);
      }
    })();
  }, []);

  return (
    <section>
      <div className="p-4 rounded-2xl bg-slate-900/60">
        <div className="text-sm text-slate-400">Revision Queue — Smart Review</div>
        <div className="mt-3 grid grid-cols-3 gap-3">
          {problems.map((p, i) => (
            <div key={i} className="p-3 rounded-xl bg-gradient-to-br from-slate-800/40 to-slate-900/50">
              <div className="text-sm text-slate-100 font-medium">{p.title}</div>
              <div className="text-xs text-slate-400 mt-1">
                Topic: {p.topics?.join(", ")} • Difficulty: {p.difficulty}
              </div>
              <div className="mt-2 flex gap-2">
                <button className="px-2 py-1 rounded bg-slate-700/40 text-xs">Open</button>
                <button className="px-2 py-1 rounded border border-slate-700/30 text-xs">Mark Done</button>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-xs text-slate-400">
          Revision powered by spaced repetition and concept confidence.
        </div>
      </div>
    </section>
  );
}
