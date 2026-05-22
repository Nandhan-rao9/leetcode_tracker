// src/pages/Landing.jsx
import api from "../utils/api";

export default function Landing({ onUserReady }) {
  const continueDemo = () => {
    // DEMO USER — NO INGESTION
    onUserReady("nandhan_rao", false);
  };

  const initUser = async () => {
    const username = prompt("Internal username (any name)");
    const lc = prompt("LeetCode username");
    const session = prompt("LEETCODE_SESSION");
    const csrf = prompt("csrftoken");

    if (!username || !lc || !session || !csrf) {
      alert("All fields are required");
      return;
    }

    sessionStorage.setItem("active_user", username);

    await api.post("/api/user/init", {
      username,
      leetcode_username: lc,
      session,
      csrftoken: csrf,
    });

    onUserReady(username, true);
  };

  return (
    <div className="h-screen flex items-center justify-center">
      <div className="space-y-4 text-center">
        <button
          onClick={continueDemo}
          className="px-6 py-3 rounded-xl bg-cyan-500 text-black font-semibold"
        >
          Continue as Demo
        </button>

        <div className="text-slate-400">or</div>

        <button
          onClick={initUser}
          className="px-6 py-3 rounded-xl bg-slate-800 text-white"
        >
          Use My LeetCode
        </button>
      </div>
    </div>
  );
}