// src/App.js
import React, { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";
import Companies from "./pages/Companies";
import CompanyView from "./pages/CompanyView";
import Review from "./pages/Review";
import Navbar from "./components/Navbar";
import api from "./utils/api";

const USERNAME = "nandhan_rao";

export default function App() {
  const [view, setView] = useState("dashboard");
  const [topCompanies, setTopCompanies] = useState([]);
  const [activeCompany, setActiveCompany] = useState(null);
  const [companyProblems, setCompanyProblems] = useState([]);

  /* ---------------- Fetch top companies on load ---------------- */
  useEffect(() => {
    (async () => {
      try {
        const c = await api.get("/companies/top");
        setTopCompanies(Array.isArray(c) ? c : []);
      } catch (err) {
        console.error("Failed to fetch top companies", err);
        setTopCompanies([]);
      }
    })();
  }, []);

  /* ---------------- Fetch problems when company is selected ---------------- */
  useEffect(() => {
    if (!activeCompany) return;

    (async () => {
      try {
        const res = await api.get(
          `/companies/${encodeURIComponent(
            activeCompany.name
          )}?user=${USERNAME}`
        );

        // ✅ backend returns { problems: [...] }
        const problems = Array.isArray(res?.problems) ? res.problems : [];

        setCompanyProblems(problems);
        setView("company");
      } catch (err) {
        console.error("Failed to fetch company problems", err);
        setCompanyProblems([]);
        setView("company");
      }
    })();
  }, [activeCompany]);

  /* ---------------- Back handler ---------------- */
  const handleBack = () => {
    setActiveCompany(null);
    setCompanyProblems([]);
    setView("dashboard"); // or "companies" if you prefer
  };

  /* ---------------- Render ---------------- */
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-[#030417] text-slate-200 font-inter">
      <div className="max-w-7xl mx-auto p-6">
        {/* ---------- Header ---------- */}
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-2xl text-black font-bold">
              LB
            </div>
            <div>
              <div className="text-white text-xl font-semibold">
                LeetBuddy — Company Prep
              </div>
              <div className="text-slate-400 text-sm">
                Focused practice, built for interviews
              </div>
            </div>
          </div>

          <Navbar view={view} setView={setView} />
        </header>

        {/* ---------- Main Views ---------- */}
        <main>
          {view === "dashboard" && (
            <Dashboard setActiveCompany={setActiveCompany} />
          )}

          {view === "companies" && (
            <Companies
              companies={topCompanies}
              setActiveCompany={setActiveCompany}
            />
          )}

          {view === "company" && activeCompany && (
            <CompanyView
              activeCompany={activeCompany}
              problems={companyProblems}
              onBack={handleBack}
            />
          )}

          {view === "review" && <Review />}
        </main>

        {/* ---------- Footer ---------- */}
        <footer className="mt-8 text-center text-xs text-slate-500">
          LeetBuddy • Built for focused company prep • Dark theme
        </footer>
      </div>
    </div>
  );
}
