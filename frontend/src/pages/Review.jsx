import { motion } from "framer-motion";

export default function Review() {
  return (
    <section>
      <div className="p-4 rounded-2xl bg-slate-900/60">
        <div className="text-sm text-slate-400">Revision Queue — Smart Review</div>
        <div className="mt-3 grid grid-cols-3 gap-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
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
      </div>
    </section>
  );
}
