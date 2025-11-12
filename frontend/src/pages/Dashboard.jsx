// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import CompanyCard from "../components/CompanyCard";
import api from "../utils/api";
import { mockFetch } from "../utils/mockApi"; // keep for offline fallbacks

export default function Dashboard({ setActiveCompany }) {
  const [summary, setSummary] = useState(null);
  const [topCompanies, setTopCompanies] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const s = await api.get("/api/summary");
        setSummary(s);
      } catch (err) {
        console.warn("Summary API failed, using mock", err);
        const s = await mockFetch("/api/summary");
        setSummary(s);
      }

      try {
        const c = await api.get("/api/companies/top");
        setTopCompanies(c);
      } catch (err) {
        console.warn("Top companies API failed, using mock", err);
        const c = await mockFetch("/api/companies/top");
        setTopCompanies(c);
      }
    })();
  }, []);

  return (
    <section className="animate-fadeIn">
      {/* Stats, Top Companies, Insights — same UI, unchanged */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard title="Solved" value={summary?.totalSolved ?? "—"} hint="Problems you've solved" />
        <StatCard title="Total Problems" value={summary?.totalProblems ?? "—"} hint="Indexed across companies" />
        <StatCard title="Companies" value={summary?.companies ?? "—"} hint="Companies covered in CSV data" />
      </div>

      <div className="grid grid-cols-3 gap-5">
        <div className="col-span-2 bg-slate-900/60 p-4 rounded-3xl shadow-2xl border border-slate-800/40">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-sm text-slate-400">Top Companies</div>
              <div className="text-lg text-white font-semibold">Where your efforts matter</div>
            </div>
            <div className="text-xs text-slate-400">Auto-updated from DB</div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {topCompanies.map((c) => (
              <CompanyCard key={c.name} company={c} onOpen={setActiveCompany} />
            ))}
          </div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-3xl shadow-2xl border border-slate-800/40">
          <div className="text-sm text-slate-400">Quick Actions</div>
          <div className="mt-3 space-y-3">
            <button className="w-full text-left px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-700/20 to-cyan-700/10 shadow-inner">Generate Company Plan</button>
            <button className="w-full text-left px-4 py-3 rounded-xl border border-slate-700 hover:bg-slate-800/30">Compare Companies</button>
            <button className="w-full text-left px-4 py-3 rounded-xl border border-slate-700 hover:bg-slate-800/30">Export CSV of Missing Problems</button>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 rounded-2xl bg-gradient-to-br from-slate-800/40 to-slate-900/50 shadow-inner">
        <div className="text-sm text-slate-400 mb-2">Insights</div>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Most Requested Topic</div>
            <div className="text-white font-semibold">Graphs</div>
            <div className="text-xs text-slate-400 mt-2">Top company: Google</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Your Weakest Topic</div>
            <div className="text-white font-semibold">Dynamic Programming</div>
            <div className="text-xs text-slate-400 mt-2">Confidence: 42%</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Daily Review</div>
            <div className="text-white font-semibold">3 problems</div>
            <div className="text-xs text-slate-400 mt-2">Next review in 12h</div>
          </div>
        </div>
      </div>
    </section>
  );
}
