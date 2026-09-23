import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { api } from "../api/client";
import { Card } from "../components/ui";
import type { Candidate } from "../types";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => {
      setLoading(true);
      api.get("/candidates", { params: { search: search || undefined } })
        .then((r) => setCandidates(r.data.candidates))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [search]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="relative w-80">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or email..."
            className="pl-9 pr-3 py-2 w-full text-sm rounded-lg bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
          />
        </div>
        <p className="text-xs text-slate-400">{candidates.length} candidates</p>
      </div>

      <Card className="p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface">
            <tr className="text-left text-slate-400 text-xs">
              <th className="px-5 py-3 font-medium">Name</th>
              <th className="px-5 py-3 font-medium">Location</th>
              <th className="px-5 py-3 font-medium">Experience</th>
              <th className="px-5 py-3 font-medium">Category</th>
              <th className="px-5 py-3 font-medium">Skills</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={5} className="px-5 py-8 text-center text-slate-400">Loading candidates...</td></tr>
            )}
            {!loading && candidates.length === 0 && (
              <tr><td colSpan={5} className="px-5 py-8 text-center text-slate-400">No candidates match your search.</td></tr>
            )}
            {candidates.map((c) => (
              <tr key={c.id} className="border-t border-slate-100 hover:bg-surface/60">
                <td className="px-5 py-3">
                  <Link to={`/candidates/${c.id}`} className="font-medium text-navy hover:text-accent-blue">
                    {c.name}
                  </Link>
                  <p className="text-xs text-slate-400">{c.email}</p>
                </td>
                <td className="px-5 py-3 text-slate-500">{c.location || "—"}</td>
                <td className="px-5 py-3 text-slate-500">{c.experience_years ?? 0} yrs</td>
                <td className="px-5 py-3">
                  <span className="text-xs bg-blue-50 text-accent-blue px-2 py-1 rounded-full">
                    {c.predicted_category || "Unclassified"}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <div className="flex flex-wrap gap-1">
                    {c.skills.slice(0, 3).map((s) => (
                      <span key={s} className="text-[11px] bg-surface px-2 py-0.5 rounded-full text-slate-500">{s}</span>
                    ))}
                    {c.skills.length > 3 && <span className="text-[11px] text-slate-400">+{c.skills.length - 3}</span>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
