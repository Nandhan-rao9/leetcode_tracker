// src/App.js
import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Companies from "./pages/Companies";
import CompanyView from "./pages/CompanyView";
import Review from "./pages/Review";
import Navbar from "./components/Navbar";
import api from "./utils/api";

function AppLayout() {
  const [topCompanies, setTopCompanies] = useState([]);
  const [activeCompany, setActiveCompany] = useState(null);
  const [companyProblems, setCompanyProblems] = useState([]);

  useEffect(() => {
    loadTopCompanies();
  }, []);

  const loadTopCompanies = async () => {
    try {
      const companies = await api.get("/companies/top");
      setTopCompanies(Array.isArray(companies) ? companies : []);
    } catch (err) {
      console.error("Failed to fetch companies", err);
    }
  };

  useEffect(() => {
    if (activeCompany) {
      loadCompanyProblems();
    }
  }, [activeCompany]);

  const loadCompanyProblems = async () => {
    try {
      const res = await api.get(
        `/companies/${encodeURIComponent(activeCompany.name)}`
      );
      setCompanyProblems(Array.isArray(res?.problems) ? res.problems : []);
    } catch (err) {
      console.error("Failed to fetch company problems", err);
    }
  };

  const handleBack = () => {
    setActiveCompany(null);
    setCompanyProblems([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-[#030417] text-slate-200 font-inter">
      <div className="max-w-7xl mx-auto p-6">
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
          <Navbar />
        </header>

        <main>
          <Routes>
            <Route
              path="/dashboard"
              element={<Dashboard setActiveCompany={setActiveCompany} />}
            />
            <Route
              path="/companies"
              element={
                <Companies
                  companies={topCompanies}
                  setActiveCompany={setActiveCompany}
                />
              }
            />
            <Route
              path="/company/:name"
              element={
                <CompanyView
                  activeCompany={activeCompany}
                  problems={companyProblems}
                  onBack={handleBack}
                />
              }
            />
            <Route path="/review" element={<Review />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>

        <footer className="mt-8 text-center text-xs text-slate-500">
          LeetBuddy • Built for focused company prep
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
