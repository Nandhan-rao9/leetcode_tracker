import React, { useState } from "react";
import api from "../utils/api";

export default function Compare({ companies }) {
  const [selected, setSelected] = useState([]);
  const [result, setResult] = useState(null);

  const toggleCompany = (c) => {
    setSelected((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );
  };

  const compare = async () => {
    if (selected.length < 2) return alert("Pick at least 2 companies");
    const res = await api.post("/api/companies/compare", { companies: selected });
    setResult(res);
  };

  return (
    <section>
      <div className="mb-4">
        <div className="text-white font-semibold">Compare Companies</div>
        <div className="text-slate-400 text-sm">Topic frequency comparison</div>
      </div>

      <div className="grid grid-cols-4 gap-2 mb-4">
        {companies.map((c) => (
          <button
            key={c.name}
            onClick={() => toggleCompany(c.name)}
            className={`px-3 py-2 rounded-lg border ${
              selected.includes(c.name)
                ? "border-cyan-400 bg-slate-800"
                : "border-slate-700 bg-slate-900"
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      <button
        onClick={compare}
        className="bg-gradient-to-r from-indigo-600 to-cyan-400 text-black font-semibold px-4 py-2 rounded-xl"
      >
        Compare
      </button>

      {result && (
        <div className="mt-6 bg-slate-900/60 p-4 rounded-2xl">
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(result).map(([company, topics]) => (
              <div key={company} className="p-4 bg-slate-800/40 rounded-xl">
                <div className="font-semibold text-white mb-2">{company}</div>
                {Object.entries(topics).map(([topic, count]) => (
                  <div key={topic} className="flex justify-between text-xs text-slate-300">
                    <span>{topic}</span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
