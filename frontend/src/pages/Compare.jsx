import React, { useState } from "react";
import api from "../utils/api";

export default function Compare({ companies }) {
  const [selected, setSelected] = useState([]);
  const [commonProblems, setCommonProblems] = useState([]);
  const [loading, setLoading] = useState(false);

  const toggleCompany = (name) => {
    setSelected(prev => prev.includes(name) ? prev.filter(x => x !== name) : [...prev, name]);
  };

  const handleCompare = async () => {
    if (selected.length < 2) return alert("Select 2+ companies to find common ground");
    setLoading(true);
    try {
      const res = await api.post("/api/companies/compare", { companies: selected });
      setCommonProblems(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="p-6 bg-slate-900/60 rounded-3xl border border-slate-800/40">
      <div className="mb-6">
        <h2 className="text-xl text-white font-bold">Company Intersection</h2>
        <p className="text-slate-400 text-sm">Find problems asked by all selected companies.</p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {companies.map(c => (
          <button 
            key={c.name}
            onClick={() => toggleCompany(c.name)}
            className={`px-4 py-2 rounded-xl text-sm transition-all border ${
              selected.includes(c.name) ? 'bg-cyan-500 text-black border-cyan-400' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      <button 
        onClick={handleCompare}
        className="px-8 py-3 bg-indigo-600 rounded-xl font-bold text-white hover:bg-indigo-500"
      >
        {loading ? "Analyzing Intersection..." : "Find Common Problems"}
      </button>

      {commonProblems.length > 0 && (
        <div className="mt-8 space-y-3">
          <h3 className="text-cyan-400 font-semibold">{commonProblems.length} Shared Problems Found</h3>
          {commonProblems.map((p, i) => (
            <div key={i} className="flex justify-between items-center p-4 bg-slate-800/40 rounded-xl border border-slate-700/30">
              <div>
                <div className="text-white font-medium">{p.title}</div>
                <div className="text-xs text-slate-500">{p.difficulty} • {p.all_topics?.join(", ")}</div>
              </div>
              <a href={p.link} target="_blank" rel="noreferrer" className="text-cyan-400 text-xs hover:underline">Solve Now →</a>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}