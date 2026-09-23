import React, { useEffect, useState } from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";
import { api } from "../api/client";
import { Card } from "../components/ui";

const COLORS = ["#2563EB", "#14B8A6", "#F59E0B", "#8B5CF6", "#F43F5E", "#0EA5E9", "#64748B"];

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<any[]>([]);
  const [funnel, setFunnel] = useState<any[]>([]);
  const [histogram, setHistogram] = useState<any[]>([]);
  const [positionWise, setPositionWise] = useState<any[]>([]);

  useEffect(() => {
    api.get("/analytics/trends").then((r) => setTrends(r.data.trends));
    api.get("/analytics/category-distribution").then((r) => setDistribution(r.data.distribution));
    api.get("/analytics/position-funnel").then((r) => setFunnel(r.data.funnel));
    api.get("/analytics/score-histogram").then((r) => setHistogram(r.data.histogram));
    api.get("/analytics/position-wise").then((r) => setPositionWise(r.data.positions));
  }, []);

  function exportCsv() {
    window.open("/api/analytics/export", "_blank");
  }

  const shortlistRate = (() => {
    const total = funnel.reduce((sum, f) => sum + f.count, 0);
    const shortlisted = funnel.find((f) => f.status === "Shortlisted")?.count ?? 0;
    return total ? Math.round((shortlisted / total) * 100) : 0;
  })();

  return (
    <div className="space-y-5">
      <div className="flex justify-end">
        <button onClick={exportCsv} className="text-sm bg-navy text-white px-4 py-2 rounded-lg hover:bg-navy-light">
          Export CSV
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <Card>
          <h3 className="font-display font-semibold mb-4">Applications over time</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#2563EB" fill="#2563EB33" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-display font-semibold mb-4">Category distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={distribution} dataKey="count" nameKey="category" outerRadius={80} label>
                {distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-display font-semibold mb-4">Match score histogram</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={histogram}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#14B8A6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-display font-semibold mb-4">Status funnel</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={funnel} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F1F5F9" />
              <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
              <YAxis type="category" dataKey="status" tick={{ fontSize: 11 }} width={90} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="lg:col-span-2">
          <h3 className="font-display font-semibold mb-4">Position-wise applicants & avg score</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={positionWise}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="title" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="applicants" name="Applicants" fill="#2563EB" radius={[4, 4, 0, 0]} />
              <Bar dataKey="avg_score" name="Avg Score %" fill="#14B8A6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-display font-semibold mb-2">Shortlist rate</h3>
          <p className="font-display font-semibold text-3xl text-navy">{shortlistRate}%</p>
          <p className="text-xs text-slate-400 mt-1">of all applications reach Shortlisted or beyond</p>
        </Card>
      </div>
    </div>
  );
}
