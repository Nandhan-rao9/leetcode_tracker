import CompanyCard from "../components/CompanyCard";

export default function Companies({ companies, setActiveCompany }) {
  return (
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
        {companies.map((c) => (
          <CompanyCard key={c.name} company={c} onOpen={setActiveCompany} />
        ))}
        <div className="col-span-4 text-sm text-slate-500 mt-2">Showing top companies — the full list is fetched from your backend.</div>
      </div>
    </section>
  );
}
