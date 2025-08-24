import { useState } from "react";

export default function Filters({ onChange, initial={} }) {
  const [q, setQ] = useState(initial.search || "");
  const [diff, setDiff] = useState(initial.difficulty || "");
  const [tag, setTag] = useState(initial.tag || "");

  return (
    <div className="filters">
      <input
        placeholder="Search title…"
        value={q}
        onChange={(e)=>setQ(e.target.value)}
        onKeyDown={(e)=> e.key==="Enter" && onChange({ search: q, difficulty: diff || undefined, tag: tag || undefined })}
      />
      <select value={diff} onChange={(e)=>{ setDiff(e.target.value); onChange({ search: q, difficulty: e.target.value || undefined, tag: tag || undefined }); }}>
        <option value="">Difficulty</option>
        <option>Easy</option><option>Medium</option><option>Hard</option>
      </select>
      <input
        placeholder="Tag (e.g., Array)"
        value={tag}
        onChange={(e)=>{ setTag(e.target.value) }}
        onKeyDown={(e)=> e.key==="Enter" && onChange({ search: q, difficulty: diff || undefined, tag: tag || undefined })}
      />
      <button onClick={()=> onChange({ search: q || undefined, difficulty: diff || undefined, tag: tag || undefined })}>Apply</button>
    </div>
  );
}
