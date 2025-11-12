// src/pages/CompanyView.jsx
import React from "react";
import ProblemRow from "../components/ProblemRow";

export default function CompanyView({ activeCompany, problems = [], setView }) {
  return (
    <section>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-white font-semibold">{activeCompany.name} — Problem Bank</div>
          <div className="text-slate-400 text-sm">{activeCompany.count ?? problems.length} indexed problems • Readiness {Math.round((activeCompany.ready ?? 0) * 100)}%</div>
        </div>
        <div>
          <button onClick={() => setView("companies")} className="px-3 py-1 rounded-md bg-slate-800/30">Back</button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-slate-900/60 p-4 rounded-2xl shadow-inner">
          <div className="text-sm text-slate-400 mb-3">Top unsolved problems</div>
          <div className="space-y-2">
            {problems.map((p) => (
              <ProblemRow key={p.title || p.id || p.link} p={{
                id: p.slug || p.link || p.title,
                title: p.title,
                difficulty: p.difficulty,
                topics: p.all_topics || [],
                num_occur: p.num_occur || 0
              }} />
            ))}
          </div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-2xl">
          <div className="text-sm text-slate-400">Generate Plan</div>
          <div className="mt-3 space-y-3">
            <select className="w-full p-2 rounded-md bg-slate-800/40">
              <option>7-day: Focused</option>
              <option>14-day: Balanced</option>
              <option>30-day: Deep</option>
            </select>
            <div className="flex gap-2">
              <input type="number" defaultValue={10} className="w-1/2 p-2 rounded-md bg-slate-800/40" />
              <select className="w-1/2 p-2 rounded-md bg-slate-800/40">
                <option>Include solved</option>
                <option>Unsolved only</option>
              </select>
            </div>
            <button className="w-full py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-400 text-black font-semibold">Create Plan</button>
          </div>
        </div>
      </div>
    </section>
  );
}
