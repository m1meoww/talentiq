import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const hasToken = !!localStorage.getItem("talentiq_token");
  if (!user && !hasToken) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
