import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, StatusBadge } from "../components/ui";
import { api } from "../api/client";
import type { Position } from "../types";

export default function PositionDetailPage() {
  const { id } = useParams();
  const [position, setPosition] = useState<Position | null>(null);

  useEffect(() => {
    api.get(`/positions/${id}`).then((r) => setPosition(r.data));
  }, [id]);

  if (!position) return <p className="text-slate-400 text-sm">Loading position...</p>;

  return (
    <div className="space-y-5">
      <Card>
        <div className="flex items-start justify-between mb-3">
          <div>
            <h2 className="font-display font-semibold text-lg text-navy">{position.title}</h2>
            <p className="text-sm text-slate-400">{position.department} · {position.location} · {position.employment_type}</p>
          </div>
          <StatusBadge status={position.status} />
        </div>
        <p className="text-sm text-slate-600 mb-3">{position.description}</p>
        <p className="text-sm text-slate-600 mb-3"><b>Requirements:</b> {position.requirements}</p>
        <div className="flex flex-wrap gap-2">
          {position.preferred_skills.map((s) => (
            <span key={s} className="text-xs bg-surface px-2.5 py-1 rounded-full text-slate-600">{s}</span>
          ))}
        </div>
      </Card>

      <Card className="p-0 overflow-hidden">
        <div className="p-5 pb-0">
          <h3 className="font-display font-semibold mb-1">Live applicant ranking</h3>
          <p className="text-xs text-slate-400 mb-4">Recomputed against current resume text using cosine similarity.</p>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-surface">
            <tr className="text-left text-slate-400 text-xs">
              <th className="px-5 py-3 font-medium">Rank</th>
              <th className="px-5 py-3 font-medium">Candidate</th>
              <th className="px-5 py-3 font-medium">Match</th>
              <th className="px-5 py-3 font-medium">Skill</th>
              <th className="px-5 py-3 font-medium">Experience</th>
              <th className="px-5 py-3 font-medium">Education</th>
            </tr>
          </thead>
          <tbody>
            {(position.rankings ?? []).length === 0 && (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-slate-400">No applicants yet for this position.</td></tr>
            )}
            {(position.rankings ?? []).map((r, i) => (
              <tr key={r.candidate_id} className="border-t border-slate-100">
                <td className="px-5 py-3 text-slate-400">#{i + 1}</td>
                <td className="px-5 py-3">
                  <Link to={`/candidates/${r.candidate_id}`} className="font-medium text-navy hover:text-accent-blue">
                    {r.candidate_name}
                  </Link>
                </td>
                <td className="px-5 py-3 font-medium text-navy">{r.overall_match}%</td>
                <td className="px-5 py-3 text-slate-500">{r.skill_score}%</td>
                <td className="px-5 py-3 text-slate-500">{r.experience_score}%</td>
                <td className="px-5 py-3 text-slate-500">{r.education_score}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
