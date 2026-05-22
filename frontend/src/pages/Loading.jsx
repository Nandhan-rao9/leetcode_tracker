import { useEffect } from "react";
import api from "../utils/api";

export default function Loading({ setView }) {
  const user = sessionStorage.getItem("active_user");

  useEffect(() => {
    const id = setInterval(async () => {
      const res = await api.get(`/api/user/status/${user}`);
      if (res.status === "ready") {
        clearInterval(id);
        setView("dashboard");
      }
    }, 2500);

    return () => clearInterval(id);
  }, []);

  return (
    <div className="h-screen flex items-center justify-center">
      Fetching & indexing your LeetCode data…
    </div>
  );
}
