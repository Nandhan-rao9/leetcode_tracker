import React, { createContext, useContext, useState, useEffect } from "react";
import api, { setAccessToken } from "../utils/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessTokenState] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await api.get("/auth/me");
      setUser(userData);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.post("/auth/login", { email, password });
    setAccessToken(response.accessToken);
    setAccessTokenState(response.accessToken);
    setUser(response.user);
    return response;
  };

  const register = async (email, password, username, leetcodeData = {}) => {
    const response = await api.post("/auth/register", {
      email,
      password,
      username,
      ...leetcodeData,
    });
    return response;
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      setAccessToken(null);
      setAccessTokenState(null);
    }
  };

  const value = {
    user,
    loading,
    accessToken,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
