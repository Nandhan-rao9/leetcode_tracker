export default function Navbar({ view, setView }) {
  return (
    <nav className="flex items-center gap-3">
      {["dashboard", "companies", "review"].map((v) => (
        <button
          key={v}
          onClick={() => setView(v)}
          className={`px-3 py-1 rounded-md text-sm ${
            view === v ? "bg-slate-800/40" : "hover:bg-slate-800/30"
          }`}
        >
          {v.charAt(0).toUpperCase() + v.slice(1)}
        </button>
      ))}
      <div className="ml-4 bg-slate-800/30 rounded-full px-3 py-2 text-xs">
        Dark • Auto
      </div>
    </nav>
  );
}
