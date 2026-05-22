// src/hooks/useSessionState.js
import { useState, useEffect } from "react";

export function useSessionState(key, initialValue) {
  const [state, setState] = useState(() => {
    const saved = sessionStorage.getItem(key);
    return saved ? JSON.parse(saved) : initialValue;
  });

  useEffect(() => {
    sessionStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState];
}