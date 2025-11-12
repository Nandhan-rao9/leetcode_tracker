// src/App.js
import React, { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";
import Companies from "./pages/Companies";
import CompanyView from "./pages/CompanyView";
import Review from "./pages/Review";
import Navbar from "./components/Navbar";
import api from "./utils/api";

export default function App() {
  const [view, setView] = useState("dashboard");
  const [topCompanies, setTopCompanies] = useState([]);
  const [activeCompany, setActiveCompany] = useState(null);
  const [companyProblems, setCompanyProblems] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const c = await api.get("/api/companies/top");
        setTopCompanies(c);
      } catch (err) {
        console.error("Failed to fetch top companies — using empty list", err);
        setTopCompanies([]);
      }
    })();
  }, []);

  useEffect(() => {
    if (!activeCompany) return;
    (async () => {
      try {
        // encode company name so spaces are handled
        const res = await api.get(`/api/companies/${encodeURIComponent(activeCompany.name)}`);
        setCompanyProblems(res.problems || res);
        setView("company");
      } catch (err) {
        console.error("Failed to fetch company problems", err);
        setCompanyProblems([]);
        setView("company");
      }
    })();
  }, [activeCompany]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-[#030417] text-slate-200 font-inter">
      <div className="max-w-7xl mx-auto p-6">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-2xl text-black font-bold">
              LB
            </div>
            <div>
              <div className="text-white text-xl font-semibold">LeetBuddy — Company Prep</div>
              <div className="text-slate-400 text-sm">Focused practice, built for interviews</div>
            </div>
          </div>
          <Navbar view={view} setView={setView} />
        </header>

        <main>
          {view === "dashboard" && <Dashboard setActiveCompany={setActiveCompany} />}
          {view === "companies" && <Companies companies={topCompanies} setActiveCompany={setActiveCompany} />}
          {view === "company" && activeCompany && (
            <CompanyView activeCompany={activeCompany} problems={companyProblems} setView={setView} />
          )}
          {view === "review" && <Review />}
        </main>

        <footer className="mt-8 text-center text-xs text-slate-500">
          LeetBuddy • Built for focused company prep • Dark theme
        </footer>
      </div>
    </div>
  );
}
