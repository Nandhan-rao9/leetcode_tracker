import React, { useEffect, useState } from "react";
import api from "../utils/api";

export default function Review() {
  const [problems, setProblems] = useState([]);
  const [completed, setCompleted] = useState({});

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(
          "/api/review/today?user=nandhan_rao"
        );
        setProblems(Array.isArray(res) ? res : []);
      } catch (err) {
        console.error("Review fetch failed", err);
        setProblems([]);
      }
    })();
  }, []);

  const toggleComplete = (slug) => {
    setCompleted((prev) => ({ ...prev, [slug]: !prev[slug] }));
  };

  const diffColor = (d) => {
    if (d === "Easy") return "text-green-400";
    if (d === "Medium") return "text-yellow-400";
    if (d === "Hard") return "text-red-400";
    return "text-slate-400";
  };

  return (
    <section className="animate-fadeIn">
      <h2 className="text-white text-xl font-bold mb-4">
        Daily Review
      </h2>

      {problems.length === 0 && (
        <div className="text-slate-400">
          Nothing to review today
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {problems.map((p) => (
          <div
            key={p.slug}
            className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/40 hover:bg-slate-800/50 transition"
          >
            {/* Title */}
            <div
              className="cursor-pointer"
              onClick={() => window.open(p.link, "_blank")}
            >
              <div
                className={`font-semibold ${
                  completed[p.slug]
                    ? "line-through text-slate-500"
                    : "text-white"
                }`}
              >
                {p.title}
              </div>

              {/* Meta */}
              <div className="mt-1 text-xs flex flex-wrap gap-3">
                <span className={diffColor(p.difficulty)}>
                  {p.difficulty}
                </span>

                {p.acRate != null && (
                  <span className="text-slate-400">
                    AC {p.acRate}%
                  </span>
                )}

                {p.paidOnly && (
                  <span className="text-purple-400">
                    Premium
                  </span>
                )}
              </div>

              {/* Topics */}
              {p.topics?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {p.topics.slice(0, 4).map((t) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 text-[10px] rounded-full bg-slate-800 text-slate-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="mt-4 flex justify-between items-center">
              <div className="text-xs text-slate-500">
                {p.indexed ? "Indexed" : "Not indexed"}
              </div>

              <button
                onClick={() => toggleComplete(p.slug)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold ${
                  completed[p.slug]
                    ? "bg-green-500/20 text-green-400"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
              >
                {completed[p.slug] ? "✓ Done" : "Mark"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
