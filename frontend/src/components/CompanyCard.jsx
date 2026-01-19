export default function CompanyCard({ company, onOpen }) {
  return (
    <div
      onClick={() => onOpen(company)}
      className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/40 cursor-pointer hover:bg-slate-800"
    >
      <div className="text-white font-semibold mb-1">
        {company.name}
      </div>

      <div className="text-xs text-slate-400">
        {company.commonProblems} common problems
      </div>

      <div className="mt-3">
        <div className="text-xs text-slate-400 mb-1">
          Interview Readiness
        </div>
        <div className="w-full h-2 rounded bg-slate-700 overflow-hidden">
          <div
            className="h-full bg-cyan-400"
            style={{ width: `${company.readiness}%` }}
          />
        </div>
        <div className="text-xs text-slate-400 mt-1">
          {company.readiness}%
        </div>
      </div>
    </div>
  );
}
