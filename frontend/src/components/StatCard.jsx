import { motion } from "framer-motion";

export default function StatCard({ title, value, hint }) {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.02 }}
      className="bg-gradient-to-br from-slate-800/80 to-slate-900/70 p-4 rounded-2xl shadow-2xl transform-gpu"
    >
      <div className="text-sm text-slate-400">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-400">{hint}</div>}
    </motion.div>
  );
}
