import React, { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api/client";
import type { AppUser } from "../types";

interface AuthContextValue {
  user: AppUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, role: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(() => {
    const raw = localStorage.getItem("talentiq_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("talentiq_token");
    if (token && !user) {
      api.get("/auth/me").then((res) => setUser(res.data.user)).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email: string, password: string) {
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      localStorage.setItem("talentiq_token", res.data.token);
      localStorage.setItem("talentiq_user", JSON.stringify(res.data.user));
      setUser(res.data.user);
    } finally {
      setLoading(false);
    }
  }

  async function register(name: string, email: string, password: string, role: string) {
    setLoading(true);
    try {
      const res = await api.post("/auth/register", { name, email, password, role });
      localStorage.setItem("talentiq_token", res.data.token);
      localStorage.setItem("talentiq_user", JSON.stringify(res.data.user));
      setUser(res.data.user);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("talentiq_token");
    localStorage.removeItem("talentiq_user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
