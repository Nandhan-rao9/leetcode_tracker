export default function ProblemRow({ p }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-800/50 transition-colors">
      <div>
        <div className="text-sm font-medium text-white">{p.title}</div>
        <div className="text-xs text-slate-400">
          {p.topics.join(" • ")} • {p.difficulty}
        </div>
      </div>
      <div className="text-xs text-slate-300">{p.num_occur} occ</div>
    </div>
  );
}
