import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

// LeetBuddy UI v2 - Single-file React component preview
// Tailwind-first design (expects Tailwind + framer-motion + shadcn available)
// Default export: App component

const mockFetch = (path, delay = 400) =>
  new Promise((res) =>
    setTimeout(() => {
      if (path === "/api/summary")
        return res({ totalSolved: 253, totalProblems: 1263, companies: 187 });
      if (path === "/api/companies/top")
        return res([
          { name: "Amazon", count: 412, ready: 0.82 },
          { name: "Google", count: 348, ready: 0.54 },
          { name: "Meta", count: 295, ready: 0.33 },
          { name: "Microsoft", count: 210, ready: 0.47 },
        ]);
      if (path.startsWith("/api/companies/"))
        return res({ problems: Array.from({ length: 8 }, (_, i) => ({
          id: `${path}-p-${i}`,
          title: `Sample Problem ${i + 1}`,
          difficulty: ["Easy", "Medium", "Hard"][i % 3],
          topics: ["Arrays", "DP", "Graphs"].slice(0, (i % 3) + 1),
          num_occur: (i + 1) * 23,
        })) });
      return res({});
    }, delay)
  );

function StatCard({ title, value, hint }) {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.02 }}
      className="bg-gradient-to-br from-slate-800/80 to-slate-900/70 p-4 rounded-2xl shadow-2xl transform-gpu"
    >
      <div className="text-sm text-slate-400">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-400">{hint}</div>}
    </motion.div>
  );
}

function CompanyCard({ company, onOpen }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ rotateX: -4, scale: 1.016 }}
      className="group bg-gradient-to-tr from-[#071028]/60 to-[#0b1b2b]/60 p-4 rounded-3xl shadow-2xl border border-slate-800/40 cursor-pointer"
      onClick={() => onOpen(company)}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-white font-semibold text-lg">{company.name}</div>
          <div className="text-slate-400 text-xs">{company.count} common problems</div>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-xs text-slate-400">Readiness</div>
          <div className="mt-1 w-28 h-3 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-3 rounded-full"
              style={{ width: `${Math.round(company.ready * 100)}%`, background: "linear-gradient(90deg,#00dfd8,#7c5cff)" }}
            />
          </div>
          <div className="text-xs text-slate-300 mt-1">{Math.round(company.ready * 100)}%</div>
        </div>
      </div>
    </motion.div>
  );
}

function ProblemRow({ p }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-800/50 transition-colors">
      <div>
        <div className="text-sm font-medium text-white">{p.title}</div>
        <div className="text-xs text-slate-400">{p.topics.join(' • ')} • {p.difficulty}</div>
      </div>
      <div className="text-xs text-slate-300">{p.num_occur} occ</div>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("dashboard");
  const [summary, setSummary] = useState(null);
  const [topCompanies, setTopCompanies] = useState([]);
  const [activeCompany, setActiveCompany] = useState(null);
  const [companyProblems, setCompanyProblems] = useState([]);

  useEffect(() => {
    (async () => {
      const s = await mockFetch("/api/summary");
      setSummary(s);
      const c = await mockFetch("/api/companies/top");
      setTopCompanies(c);
    })();
  }, []);

  useEffect(() => {
    if (!activeCompany) return;
    (async () => {
      const res = await mockFetch(`/api/companies/${activeCompany.name}`);
      setCompanyProblems(res.problems);
      setView("company");
    })();
  }, [activeCompany]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-[#030417] text-slate-200 font-inter">
      <div className="max-w-7xl mx-auto p-6">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-2xl text-black font-bold">LB</div>
            <div>
              <div className="text-white text-xl font-semibold">LeetBuddy — Company Prep</div>
              <div className="text-slate-400 text-sm">Focused practice, built for interviews</div>
            </div>
          </div>

          <nav className="flex items-center gap-3">
            <button onClick={() => setView('dashboard')} className={`px-3 py-1 rounded-md text-sm ${view === 'dashboard' ? 'bg-slate-800/40' : 'hover:bg-slate-800/30'}`}>Dashboard</button>
            <button onClick={() => setView('companies')} className={`px-3 py-1 rounded-md text-sm ${view === 'companies' ? 'bg-slate-800/40' : 'hover:bg-slate-800/30'}`}>Companies</button>
            <button onClick={() => setView('review')} className={`px-3 py-1 rounded-md text-sm ${view === 'review' ? 'bg-slate-800/40' : 'hover:bg-slate-800/30'}`}>Revision</button>
            <div className="ml-4 bg-slate-800/30 rounded-full px-3 py-2 text-xs">Dark • Auto</div>
          </nav>
        </header>

        <main>
          {view === 'dashboard' && (
            <section>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <StatCard title="Solved" value={summary ? summary.totalSolved : '—'} hint="Problems you've solved" />
                <StatCard title="Total Problems" value={summary ? summary.totalProblems : '—'} hint="Indexed across companies" />
                <StatCard title="Companies" value={summary ? summary.companies : '—'} hint="Companies covered in CSV data" />
              </div>

              <div className="grid grid-cols-3 gap-5">
                <div className="col-span-2 bg-slate-900/60 p-4 rounded-3xl shadow-2xl border border-slate-800/40">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-sm text-slate-400">Top Companies</div>
                      <div className="text-lg text-white font-semibold">Where your efforts matter</div>
                    </div>
                    <div className="text-xs text-slate-400">Auto-updated from CSVs</div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {topCompanies.map((c) => (
                      <CompanyCard key={c.name} company={c} onOpen={(co) => setActiveCompany(co)} />
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
          )}

          {view === 'companies' && (
            <section>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-white font-semibold">All Companies</div>
                  <div className="text-slate-400 text-sm">Browse company problem banks and generate plans</div>
                </div>
                <div>
                  <input placeholder="Search companies..." className="bg-slate-900/40 px-3 py-2 rounded-md text-sm text-slate-200 outline-none" />
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                {topCompanies.map((c) => (
                  <CompanyCard key={c.name} company={c} onOpen={(co) => setActiveCompany(co)} />
                ))}
                {/* show more placeholder */}
                <div className="col-span-4 text-sm text-slate-500 mt-2">Showing top companies — the full list is fetched from your backend.</div>
              </div>
            </section>
          )}

          {view === 'company' && activeCompany && (
            <section>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-white font-semibold">{activeCompany.name} — Problem Bank</div>
                  <div className="text-slate-400 text-sm">{activeCompany.count} indexed problems • Readiness {Math.round(activeCompany.ready*100)}%</div>
                </div>
                <div>
                  <button onClick={() => setView('companies')} className="px-3 py-1 rounded-md bg-slate-800/30">Back</button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2 bg-slate-900/60 p-4 rounded-2xl shadow-inner">
                  <div className="text-sm text-slate-400 mb-3">Top unsolved problems</div>
                  <div className="space-y-2">
                    {companyProblems.map((p) => (
                      <ProblemRow key={p.id} p={p} />
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
                    <div className="text-xs text-slate-400 mt-2">Plans are personalized using your solved/unsolved data and company frequencies.</div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {view === 'review' && (
            <section>
              <div className="p-4 rounded-2xl bg-slate-900/60">
                <div className="text-sm text-slate-400">Revision Queue — Smart Review</div>
                <div className="mt-3 grid grid-cols-3 gap-3">
                  {/* Mini cards for today's due problems */}
                  {[1,2,3,4,5,6].map((i)=> (
                    <motion.div key={i} whileHover={{ y: -6 }} className="p-3 rounded-xl bg-gradient-to-br from-slate-800/40 to-slate-900/50">
                      <div className="text-sm text-slate-100 font-medium">Problem {i}</div>
                      <div className="text-xs text-slate-400 mt-1">Topic: DP • Difficulty: Medium</div>
                      <div className="mt-2 flex gap-2">
                        <button className="px-2 py-1 rounded bg-slate-700/40 text-xs">Open</button>
                        <button className="px-2 py-1 rounded border border-slate-700/30 text-xs">Mark Done</button>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <div className="mt-4 text-xs text-slate-400">Revision powered by spaced-repetition and concept-confidence.</div>
              </div>
            </section>
          )}
        </main>

        <footer className="mt-8 text-center text-xs text-slate-500">LeetBuddy • Built for focused company prep • Dark theme</footer>
      </div>
    </div>
  );
}
