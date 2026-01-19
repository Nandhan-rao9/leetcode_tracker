import React, { useEffect, useState } from "react";
import api from "../utils/api";

export default function CompanyView({ activeCompany, problems, onBack }) {
  const storageKey = `plan_${activeCompany.name}`;

  const [plan, setPlan] = useState(() => {
    const saved = sessionStorage.getItem(storageKey);
    return saved ? JSON.parse(saved) : [];
  });

  const [num, setNum] = useState(10);
  const [includeSolved, setIncludeSolved] = useState(false);
  const [selectedDiffs, setSelectedDiffs] = useState(["Easy", "Medium", "Hard"]);
  const [loading, setLoading] = useState(false);
  const [doneProblems, setDoneProblems] = useState({});

  useEffect(() => {
    if (plan.length) {
      sessionStorage.setItem(storageKey, JSON.stringify(plan));
    }
  }, [plan, storageKey]);

  const toggleDiff = (d) => {
    setSelectedDiffs((prev) =>
      prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d]
    );
  };

  const diffColor = (d) => {
  if (d === "Easy") return "text-green-400";
  if (d === "Medium") return "text-yellow-400";
  if (d === "Hard") return "text-red-400";
  return "text-slate-400";
};

  const generatePlan = async () => {
    try {
      setLoading(true);
      const res = await api.post(
        `/api/companies/${activeCompany.name}/smart_plan`,
        {
          user: "nandhan_rao",
          num,
          include_solved: includeSolved,
          difficulties: selectedDiffs,
        }
      );

      // ✅ backend returns array
      setPlan(Array.isArray(res) ? res : []);
    } catch (err) {
      console.error("Error generating plan:", err);
      setPlan([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <button onClick={onBack} className="text-cyan-400 mb-4">
        ← Back
      </button>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <h2 className="text-white font-bold mb-4">
            {activeCompany.name} Plan
          </h2>

          {plan.map((p) => (
  <div
    key={p.slug}
    className="p-4 mb-3 rounded-2xl bg-slate-900/60 border border-slate-800/40 hover:bg-slate-800/50 transition"
  >
    {/* Clickable content */}
    <div
      className="cursor-pointer"
      onClick={() => window.open(p.link, "_blank")}
    >
      {/* Title */}
      <div
        className={`font-semibold ${
          doneProblems[p.slug]
            ? "line-through text-slate-500"
            : "text-white"
        }`}
      >
        {p.title}
      </div>

      {/* Meta row */}
      <div className="mt-1 text-xs flex flex-wrap gap-3">
        <span className={diffColor(p.difficulty)}>
          {p.difficulty}
        </span>

        {p.acRate != null && (
          <span className="text-slate-400">
            AC {p.acRate}%
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
    <div className="mt-4 flex justify-end">
      <button
        onClick={() =>
          setDoneProblems((prev) => ({
            ...prev,
            [p.slug]: !prev[p.slug],
          }))
        }
        className={`px-3 py-1 rounded-lg text-xs font-semibold ${
          doneProblems[p.slug]
            ? "bg-green-500/20 text-green-400"
            : "bg-slate-700 text-slate-300 hover:bg-slate-600"
        }`}
      >
        {doneProblems[p.slug] ? "✓ Done" : "Mark"}
      </button>
    </div>
  </div>
))}
        </div>

        <div>
          <div className="mb-3 text-white font-semibold">Settings</div>

          <div className="flex gap-2 mb-3">
            {["Easy", "Medium", "Hard"].map((d) => (
              <button
                key={d}
                onClick={() => toggleDiff(d)}
                className={`px-2 py-1 text-xs border ${
                  selectedDiffs.includes(d)
                    ? "border-cyan-400"
                    : "border-slate-600"
                }`}
              >
                {d}
              </button>
            ))}
          </div>

          <label className="text-xs">
            <input
              type="checkbox"
              checked={includeSolved}
              onChange={(e) => setIncludeSolved(e.target.checked)}
            />{" "}
            Include solved
          </label>

          <button
            onClick={generatePlan}
            disabled={loading}
            className="block mt-4 w-full bg-cyan-500 text-black py-2 rounded"
          >
            {loading ? "Generating..." : "Generate Plan"}
          </button>
        </div>
      </div>
    </section>
  );
}
