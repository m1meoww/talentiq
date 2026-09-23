import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Candidate");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await register(name, email, password, role);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Could not create your account.");
    }
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-10 h-10 rounded-lg bg-navy flex items-center justify-center font-display font-bold text-accent-teal mx-auto mb-3">T</div>
          <h1 className="font-display font-semibold text-xl text-navy">Create your account</h1>
          <p className="text-sm text-slate-500 mt-1">Start evaluating candidates with TalentIQ</p>
        </div>

        <form onSubmit={submit} className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          {error && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</p>}
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Full name</label>
            <input required value={name} onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/30" />
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/30" />
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue/30" />
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">I am a</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white">
              <option value="Candidate">Candidate</option>
              <option value="HR">HR / Recruiter</option>
              <option value="Admin">Admin</option>
            </select>
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-accent-blue text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-600 transition disabled:opacity-60">
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          Already have an account? <Link to="/login" className="text-accent-blue font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
