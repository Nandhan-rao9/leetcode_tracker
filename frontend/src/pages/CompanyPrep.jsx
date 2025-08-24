import { useEffect, useMemo, useState } from "react";
import { fetchCompaniesTop, fetchProblems } from "../api/problems";
import CompanyBarChart from "../components/CompanyBarChart";
import Filters from "../components/Filters";
import ProblemRow from "../components/ProblemRow";

export default function CompanyPrep() {
  const [companies, setCompanies] = useState([]);
  const [selected, setSelected] = useState("");
  const [problems, setProblems] = useState({ items: [], total: 0 });
  const [filters, setFilters] = useState({});

  useEffect(() => {
    (async ()=> {
      const top = await fetchCompaniesTop({ limit: 20 });
      setCompanies(top || []);
      if (top?.length) setSelected(top[0].company);
    })();
  }, []);

  useEffect(() => {
    (async ()=> {
      if (!selected) return;
      const p = await fetchProblems({
        company: selected,
        search: filters.search,
        difficulty: filters.difficulty,
        tag: filters.tag,
        pageSize: 200
      });
      setProblems(p);
    })();
  }, [selected, filters]);

  const chartData = useMemo(() => companies, [companies]);

  return (
    <div className="company-grid">
      <div className="left">
        <h2>Company Prep</h2>
        <p className="subtle">Pick a company to focus your prep.</p>
        <CompanyBarChart data={chartData} />
        <ul className="company-list">
          {companies.map((c) => (
            <li key={c.company}>
              <button className={c.company === selected ? "active" : ""} onClick={()=> setSelected(c.company)}>
                {c.company} <span className="count">{c.count}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="right">
        <div className="header-row">
          <h3>{selected || "Select a company"}</h3>
          <Filters onChange={setFilters} initial={{}} />
        </div>

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Problem</th>
                <th>Difficulty</th>
                <th>Tags</th>
                <th style={{textAlign:"right"}}>Company Freq</th>
                <th>Last Solved</th>
              </tr>
            </thead>
            <tbody>
              {(problems.items || []).map((item) => (
                <ProblemRow key={item._id || item.slug || item.url} item={item} />
              ))}
            </tbody>
          </table>
          {(problems.items || []).length === 0 && <div className="empty">No problems found.</div>}
        </div>
      </div>
    </div>
  );
}
