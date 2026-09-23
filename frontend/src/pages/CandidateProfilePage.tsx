import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, MatchGauge, ScoreBar, SkillChip, StatusBadge } from "../components/ui";
import { api } from "../api/client";
import type { Candidate, Application } from "../types";

type Tab = "profile" | "resume" | "ai";

export default function CandidateProfilePage() {
  const { id } = useParams();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [tab, setTab] = useState<Tab>("profile");

  useEffect(() => {
    api.get(`/candidates/${id}`).then((r) => setCandidate(r.data));
  }, [id]);

  if (!candidate) return <p className="text-slate-400 text-sm">Loading candidate profile...</p>;

  const topApplication: Application | undefined = candidate.applications?.[0];

  return (
    <div className="space-y-5">
      <Card>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-navy text-white flex items-center justify-center font-display font-semibold text-lg">
            {candidate.name?.[0]}
          </div>
          <div className="flex-1">
            <h2 className="font-display font-semibold text-lg text-navy">{candidate.name}</h2>
            <p className="text-sm text-slate-500">{candidate.email} · {candidate.location}</p>
          </div>
          <span className="text-xs bg-blue-50 text-accent-blue px-3 py-1.5 rounded-full font-medium">
            {candidate.predicted_category || "Unclassified"}
          </span>
        </div>
      </Card>

      <div className="flex gap-1 border-b border-slate-200">
        {(["profile", "resume", "ai"] as Tab[]).map((t) => (
          <button
            key={t} onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition ${
              tab === t ? "border-accent-blue text-accent-blue" : "border-transparent text-slate-500 hover:text-navy"
            }`}
          >
            {t === "profile" ? "Profile" : t === "resume" ? "Resume" : "AI Analysis"}
          </button>
        ))}
      </div>

      {tab === "profile" && (
        <div className="grid md:grid-cols-2 gap-5">
          <Card>
            <h3 className="font-display font-semibold mb-3">Education</h3>
            <p className="text-sm text-slate-600">{candidate.education || "Not provided."}</p>
          </Card>
          <Card>
            <h3 className="font-display font-semibold mb-3">Experience</h3>
            <p className="text-sm text-slate-600">{candidate.experience_years ?? 0} years overall</p>
            <p className="text-sm text-slate-500 mt-2">{candidate.summary}</p>
          </Card>
          <Card className="md:col-span-2">
            <h3 className="font-display font-semibold mb-3">Skills</h3>
            <div className="flex flex-wrap gap-2">
              {candidate.skills.map((s) => (
                <span key={s} className="text-xs bg-surface px-3 py-1.5 rounded-full text-slate-600">{s}</span>
              ))}
            </div>
          </Card>
        </div>
      )}

      {tab === "resume" && (
        <Card>
          <h3 className="font-display font-semibold mb-3">Resume file</h3>
          {candidate.resume_path ? (
            <p className="text-sm text-slate-500">
              A resume is on file at <code className="text-xs bg-surface px-1.5 py-0.5 rounded">{candidate.resume_path}</code>.
              Configure a static file route on the backend to preview/download it in-browser.
            </p>
          ) : (
            <p className="text-sm text-slate-400">No resume has been uploaded yet.</p>
          )}
        </Card>
      )}

      {tab === "ai" && (
        <div className="grid md:grid-cols-2 gap-5">
          <Card className="flex flex-col items-center justify-center">
            <MatchGauge score={topApplication?.match_score ?? 0} />
            <p className="text-xs text-slate-400 mt-3">
              {topApplication ? `Against ${topApplication.position_title}` : "No active application to score against."}
            </p>
          </Card>
          <Card className="space-y-4">
            <h3 className="font-display font-semibold">Score breakdown</h3>
            <ScoreBar label="Skill match" value={topApplication?.breakdown.skill ?? 0} />
            <ScoreBar label="Experience fit" value={topApplication?.breakdown.experience ?? 0} />
            <ScoreBar label="Education fit" value={topApplication?.breakdown.education ?? 0} />
            <ScoreBar label="Keyword overlap" value={topApplication?.breakdown.keyword ?? 0} />
          </Card>
          <Card className="md:col-span-2">
            <h3 className="font-display font-semibold mb-3">Matched vs missing skills</h3>
            <div className="flex flex-wrap gap-2">
              {(topApplication?.matched_skills ?? []).map((s) => <SkillChip key={s} label={s} matched />)}
              {(topApplication?.missing_skills ?? []).map((s) => <SkillChip key={s} label={s} matched={false} />)}
              {!topApplication && <p className="text-sm text-slate-400">No application on file yet.</p>}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
