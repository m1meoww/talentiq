import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = [
  { label: "Admin", email: "admin@talentiq.ai", password: "Admin@123" },
  { label: "HR Recruiter", email: "recruiter@talentiq.ai", password: "Recruiter@123" },
  { label: "Candidate", email: "candidate@talentiq.ai", password: "Candidate@123" },
];

export default function LoginPage() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent, overrideEmail?: string, overridePassword?: string) {
    e.preventDefault();
    setError("");
    try {
      await login(overrideEmail ?? email, overridePassword ?? password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Could not sign in. Please check your credentials.");
    }
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-10 h-10 rounded-lg bg-navy flex items-center justify-center font-display font-bold text-accent-teal mx-auto mb-3">T</div>
          <h1 className="font-display font-semibold text-xl text-navy">Welcome back</h1>
          <p className="text-sm text-slate-500 mt-1">Sign in to your TalentIQ workspace</p>
        </div>

        <form onSubmit={submit} className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          {error && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</p>}
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Password</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full bg-accent-blue text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-600 transition disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-5">
          <p className="text-xs text-slate-400 text-center mb-2">Or try a demo account</p>
          <div className="grid grid-cols-3 gap-2">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.email}
                onClick={(e) => submit(e, acc.email, acc.password)}
                className="text-xs py-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-navy font-medium"
              >
                {acc.label}
              </button>
            ))}
          </div>
        </div>

        <p className="text-center text-sm text-slate-500 mt-6">
          No account? <Link to="/register" className="text-accent-blue font-medium">Create one</Link>
        </p>
      </div>
    </div>
  );
}
