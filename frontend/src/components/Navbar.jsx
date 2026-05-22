import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="flex items-center gap-3">
      {["dashboard", "companies", "review"].map((path) => (
        <NavLink
          key={path}
          to={`/${path}`}
          className={({ isActive }) =>
            `px-3 py-1 rounded-md text-sm transition ${
              isActive ? "bg-slate-800/40" : "hover:bg-slate-800/30"
            }`
          }
        >
          {path.charAt(0).toUpperCase() + path.slice(1)}
        </NavLink>
      ))}

      <div className="ml-4 flex items-center gap-2">
        <div className="bg-slate-800/30 rounded-full px-3 py-2 text-xs">
          {user?.username || user?.email || "User"}
        </div>
        <button
          onClick={handleLogout}
          className="px-3 py-1 rounded-md text-sm bg-red-500/20 text-red-400 hover:bg-red-500/30 transition"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
