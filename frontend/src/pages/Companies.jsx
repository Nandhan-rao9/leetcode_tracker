// src/pages/Companies.jsx
import React, { useMemo, useState } from "react";
import CompanyCard from "../components/CompanyCard";

export default function Companies({ companies = [], setActiveCompany }) {
  const [query, setQuery] = useState("");

  const filteredCompanies = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return companies;

    return companies.filter((c) =>
      c.name.toLowerCase().includes(q)
    );
  }, [companies, query]);

  return (
    <section>
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-white font-semibold">All Companies</div>
          <div className="text-slate-400 text-sm">
            Browse company problem banks and generate plans
          </div>
        </div>

        {/* Search */}
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies..."
          className="bg-slate-900/40 px-3 py-2 rounded-md text-sm text-slate-200 outline-none"
        />
      </div>

      {/* Companies Grid */}
      <div className="grid grid-cols-4 gap-4">
        {filteredCompanies.length > 0 ? (
          filteredCompanies.map((c) => (
            <CompanyCard
              key={c.name}
              company={c}
              onOpen={setActiveCompany}
            />
          ))
        ) : (
          <div className="col-span-4 text-center text-slate-500 py-10">
            No companies found.
          </div>
        )}

        {filteredCompanies.length > 0 && (
          <div className="col-span-4 text-sm text-slate-500 mt-2">
            Showing {filteredCompanies.length} companies from backend data.
          </div>
        )}
      </div>
    </section>
  );
}
