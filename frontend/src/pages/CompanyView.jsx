import React, { useState } from "react";
import api from "../utils/api";

export default function CompanyView({ activeCompany, problems }) {
  const [plan, setPlan] = useState([]);
  const [num, setNum] = useState(10);
  const [includeSolved, setIncludeSolved] = useState(false);
  const [loading, setLoading] = useState(false);

  const generatePlan = async () => {
  try {
    setLoading(true);
    const res = await api.post(`/api/companies/${activeCompany.name}/smart_plan`, {
      num,
      include_solved: includeSolved,
    });
    setPlan(res);
  } catch (err) {
    console.error("Error generating plan:", err);
  } finally {
    setLoading(false);
  }
};


  return (
    <section>
      {/* --- Left side: problem bank --- */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-slate-900/60 p-4 rounded-2xl shadow-inner">
          <div className="text-sm text-slate-400 mb-3">
            Top unsolved problems
          </div>
          <div className="space-y-2">
            {problems.map((p) => (
              <div
                key={p.title}
                onClick={() => window.open(p.link, "_blank")}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-800/50 cursor-pointer transition-colors"
              >
                <div>
                  <div className="text-sm font-medium text-white">
                    {p.title}
                  </div>
                  <div className="text-xs text-slate-400">
                    {p.all_topics?.join(" • ")} • {p.difficulty}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* --- Right side: plan generator --- */}
        <div className="bg-slate-900/60 p-4 rounded-2xl">
          <div className="text-sm text-slate-400">Generate Plan</div>
          <div className="mt-3 space-y-3">
            <select className="w-full p-2 rounded-md bg-slate-800/40">
              <option>7-day: Focused</option>
              <option>14-day: Balanced</option>
              <option>30-day: Deep</option>
            </select>

            <div className="flex gap-2">
              <input
                type="number"
                value={num}
                onChange={(e) => setNum(e.target.value)}
                className="w-1/2 p-2 rounded-md bg-slate-800/40"
              />
              <select
                value={includeSolved ? "Include solved" : "Unsolved only"}
                onChange={(e) =>
                  setIncludeSolved(e.target.value === "Include solved")
                }
                className="w-1/2 p-2 rounded-md bg-slate-800/40"
              >
                <option>Unsolved only</option>
                <option>Include solved</option>
              </select>
            </div>

            <button
              onClick={generatePlan}
              disabled={loading}
              className="w-full py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-400 text-black font-semibold"
            >
              {loading ? "Generating..." : "Create Plan"}
            </button>

            <div className="text-xs text-slate-400 mt-2">
              Plans are personalized using solved/unsolved data and topic
              diversity.
            </div>

            {plan.length > 0 && (
              <div className="mt-4 bg-slate-800/50 rounded-xl p-3 text-xs text-slate-300 max-h-60 overflow-y-auto">
                <div className="font-semibold text-white mb-2">
                  Generated Plan
                </div>
                {plan.map((p, i) => (
                  <div
                    key={i}
                    onClick={() => window.open(p.link, "_blank")}
                    className="cursor-pointer hover:text-cyan-400 transition"
                  >
                    {i + 1}. {p.title} ({p.difficulty})
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
