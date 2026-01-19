// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import CompanyCard from "../components/CompanyCard";
import api from "../utils/api";

export default function Dashboard({ setActiveCompany }) {
  const [summary, setSummary] = useState(null);
  const [topCompanies, setTopCompanies] = useState([]);
  const [insights, setInsights] = useState(null); // ✅ FIX

useEffect(() => {
  (async () => {
    const user = "nandhan_rao";

    const s = await api.get(`/api/summary?user=${user}`);
    console.log("SUMMARY FROM API:", s);
    setSummary(s);

    const c = await api.get(`/api/companies/top?user=${user}`);
    console.log("COMPANIES FROM API:", c);
    setTopCompanies(c);

    const i = await api.get("/api/insights");
    console.log("INSIGHTS FROM API:", i);
    setInsights(i);
  })().catch(err => {
    console.error("Dashboard API error:", err);
  });
}, []);


  return (
    <section className="animate-fadeIn">
      {/* ---------- Stats ---------- */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard
          title="Solved"
          value={summary?.totalSolved ?? "—"}
          hint="Problems you've solved"
        />
        <StatCard
          title="Total Problems"
          value={summary?.totalProblems ?? "—"}
          hint="Indexed across companies"
        />
        <StatCard
          title="Companies"
          value={summary?.companies ?? "—"}
          hint="Companies covered"
        />
      </div>

      {/* ---------- Top Companies ---------- */}
      <div className="grid grid-cols-3 gap-5">
        <div className="col-span-2 bg-slate-900/60 p-4 rounded-3xl border border-slate-800/40">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-sm text-slate-400">Top Companies</div>
              <div className="text-lg text-white font-semibold">
                Where your efforts matter
              </div>
            </div>
            <div className="text-xs text-slate-400">Auto-updated</div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {topCompanies.map((c) => (
              <CompanyCard
                key={c.name}
                company={c}
                onOpen={setActiveCompany}
              />
            ))}
          </div>
        </div>

        {/* ---------- Quick Actions ---------- */}
        <div className="bg-slate-900/60 p-4 rounded-3xl border border-slate-800/40">
          <div className="text-sm text-slate-400">Quick Actions</div>
          <div className="mt-3 space-y-3">
            <button className="w-full px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-700/20 to-cyan-700/10">
              Generate Company Plan
            </button>
            <button className="w-full px-4 py-3 rounded-xl border border-slate-700 hover:bg-slate-800/30">
              Compare Companies
            </button>
          </div>
        </div>
      </div>

      {/* ---------- Insights ---------- */}
      <div className="mt-6 p-4 rounded-2xl bg-slate-800/40">
        <div className="text-sm text-slate-400 mb-2">Insights</div>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Most Requested Topic</div>
            <div className="text-white font-semibold">
              {insights?.most_requested_topic ?? "—"}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Your Weakest Topic</div>
            <div className="text-white font-semibold">
              {insights?.weakest_topic ?? "—"}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50">
            <div className="text-xs text-slate-400">Daily Review</div>
            <div className="text-white font-semibold">
              {insights?.daily_review_count ?? "—"} problems
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Next review in {insights?.next_review ?? "—"}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
