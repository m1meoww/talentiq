import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid,
} from "recharts";
import { api } from "../api/client";
import { Card, KPICard, StatusBadge } from "../components/ui";
import type { KPIs } from "../types";
import { Send } from "lucide-react";

const COLORS = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#F43F5E", "#0EA5E9", "#64748B"];
const SUGGESTED_PROMPTS = [
  "What are our open positions?",
  "Who is the top applicant for AI/ML Engineer?",
  "Find candidates with python and sql",
];

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatReply, setChatReply] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    api.get("/analytics/kpis").then((r) => setKpis(r.data));
    api.get("/analytics/trends").then((r) => setTrends(r.data.trends));
    api.get("/analytics/category-distribution").then((r) => setDistribution(r.data.distribution));
    api.get("/positions").then((r) => setPositions(r.data.positions.slice(0, 5)));
    api.get("/applications").then((r) => setApplications(r.data.applications.slice(0, 6)));
  }, []);

  async function sendChat(message: string) {
    setChatLoading(true);
    setChatReply(null);
    try {
      const res = await api.post("/chatbot/message", { message });
      setChatReply(res.data.reply);
    } catch {
      setChatReply("Sorry, I couldn't process that just now.");
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <KPICard label="Total Applicants" value={kpis?.total_applicants ?? "—"} />
        <KPICard label="Resumes Screened" value={kpis?.resumes_screened ?? "—"} />
        <KPICard label="Open Positions" value={kpis?.open_positions ?? "—"} />
        <KPICard label="Shortlisted" value={kpis?.shortlisted ?? "—"} />
        <KPICard label="Avg Match Score" value={kpis ? `${kpis.avg_match_score}%` : "—"} hint="live" />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h3 className="font-display font-semibold mb-4">Applicant trends</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94A3B8" />
              <YAxis tick={{ fontSize: 11 }} stroke="#94A3B8" allowDecimals={false} />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#2563EB" fill="url(#trendFill)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-display font-semibold mb-4">Candidate categories</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={distribution} dataKey="count" nameKey="category" innerRadius={45} outerRadius={75} paddingAngle={2}>
                {distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-semibold">Top job positions</h3>
            <Link to="/positions" className="text-xs text-accent-blue font-medium">View all</Link>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 text-xs">
                <th className="pb-2 font-medium">Position</th>
                <th className="pb-2 font-medium">Applicants</th>
                <th className="pb-2 font-medium">Avg Score</th>
                <th className="pb-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => (
                <tr key={p.id} className="border-t border-slate-100">
                  <td className="py-2.5">{p.title}</td>
                  <td className="py-2.5">{p.applicant_count}</td>
                  <td className="py-2.5">{p.avg_score}%</td>
                  <td className="py-2.5"><StatusBadge status={p.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-display font-semibold">Ask Talia</h3>
            <Link to="/assistant" className="text-xs text-accent-blue font-medium">Full chat</Link>
          </div>
          <div className="flex flex-wrap gap-2 mb-3">
            {SUGGESTED_PROMPTS.map((p) => (
              <button key={p} onClick={() => { setChatInput(p); sendChat(p); }}
                className="text-[11px] px-2.5 py-1.5 rounded-full bg-surface border border-slate-200 hover:bg-slate-100">
                {p}
              </button>
            ))}
          </div>
          {chatLoading && <p className="text-xs text-slate-400 mb-2">Talia is thinking...</p>}
          {chatReply && (
            <div className="bg-surface rounded-lg p-3 text-xs text-navy whitespace-pre-line mb-3">{chatReply}</div>
          )}
          <form
            onSubmit={(e) => { e.preventDefault(); if (chatInput.trim()) sendChat(chatInput); }}
            className="flex gap-2"
          >
            <input
              value={chatInput} onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask about a candidate or role..."
              className="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
            />
            <button type="submit" className="bg-navy text-white px-3 rounded-lg">
              <Send size={14} />
            </button>
          </form>
        </Card>
      </div>

      <Card>
        <h3 className="font-display font-semibold mb-4">Recent applications</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400 text-xs">
              <th className="pb-2 font-medium">Candidate</th>
              <th className="pb-2 font-medium">Position</th>
              <th className="pb-2 font-medium">Match</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((a) => (
              <tr key={a.id} className="border-t border-slate-100">
                <td className="py-2.5">{a.candidate_name}</td>
                <td className="py-2.5">{a.position_title}</td>
                <td className="py-2.5">{a.match_score}%</td>
                <td className="py-2.5"><StatusBadge status={a.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
