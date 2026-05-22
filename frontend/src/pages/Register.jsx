import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Register() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    username: "",
    leetcode_username: "",
    leetcode_session: "",
    leetcode_csrf: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showLeetCodeFields, setShowLeetCodeFields] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const leetcodeData = showLeetCodeFields
        ? {
            leetcode_username: formData.leetcode_username,
            leetcode_session: formData.leetcode_session,
            leetcode_csrf: formData.leetcode_csrf,
          }
        : {};

      await register(
        formData.email,
        formData.password,
        formData.username,
        leetcodeData
      );

      navigate("/login", {
        state: { message: "Registration successful! Please login." },
      });
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-[#030417] flex items-center justify-center p-6">
      <div className="bg-slate-900/60 p-8 rounded-3xl border border-slate-800/40 w-full max-w-md">
        <div className="flex items-center justify-center mb-6">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-2xl text-black font-bold text-2xl">
            LB
          </div>
        </div>

        <h1 className="text-2xl font-bold text-white mb-2 text-center">
          Create Account
        </h1>
        <p className="text-slate-400 text-sm mb-6 text-center">
          Join LeetBuddy to start tracking your progress
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500/40 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-slate-400 text-sm mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-slate-400 text-sm mb-2">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition"
              placeholder="your_username"
              required
            />
          </div>

          <div>
            <label className="block text-slate-400 text-sm mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition"
              placeholder="••••••••"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              Min 8 characters, include uppercase, lowercase, and number
            </p>
          </div>

          <div>
            <label className="block text-slate-400 text-sm mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="pt-2">
            <button
              type="button"
              onClick={() => setShowLeetCodeFields(!showLeetCodeFields)}
              className="text-sm text-cyan-400 hover:underline"
            >
              {showLeetCodeFields ? "− " : "+ "}
              {showLeetCodeFields
                ? "Hide LeetCode credentials"
                : "Add LeetCode credentials (optional)"}
            </button>
          </div>

          {showLeetCodeFields && (
            <div className="space-y-3 pt-2 border-t border-slate-700">
              <div>
                <label className="block text-slate-400 text-sm mb-2">
                  LeetCode Username
                </label>
                <input
                  type="text"
                  name="leetcode_username"
                  value={formData.leetcode_username}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition text-sm"
                  placeholder="leetcode_username"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">
                  Session Cookie
                </label>
                <input
                  type="text"
                  name="leetcode_session"
                  value={formData.leetcode_session}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition text-sm"
                  placeholder="LEETCODE_SESSION value"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">
                  CSRF Token
                </label>
                <input
                  type="text"
                  name="leetcode_csrf"
                  value={formData.leetcode_csrf}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white outline-none focus:border-cyan-500 transition text-sm"
                  placeholder="csrftoken value"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-indigo-500 to-cyan-400 text-black font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 transition mt-6"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-slate-400 text-sm">
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-cyan-400 hover:underline font-semibold"
          >
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
