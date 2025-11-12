import { motion } from "framer-motion";

export default function CompanyCard({ company, onOpen }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ rotateX: -4, scale: 1.016 }}
      className="group bg-gradient-to-tr from-[#071028]/60 to-[#0b1b2b]/60 p-4 rounded-3xl shadow-2xl border border-slate-800/40 cursor-pointer"
      onClick={() => onOpen(company)}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-white font-semibold text-lg">{company.name}</div>
          <div className="text-slate-400 text-xs">{company.count} common problems</div>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-xs text-slate-400">Readiness</div>
          <div className="mt-1 w-28 h-3 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-3 rounded-full"
              style={{
                width: `${Math.round(company.ready * 100)}%`,
                background: "linear-gradient(90deg,#00dfd8,#7c5cff)",
              }}
            />
          </div>
          <div className="text-xs text-slate-300 mt-1">{Math.round(company.ready * 100)}%</div>
        </div>
      </div>
    </motion.div>
  );
}
