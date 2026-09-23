import React, { useEffect, useRef, useState } from "react";
import { UploadCloud, FileText, CheckCircle2 } from "lucide-react";
import { api } from "../api/client";
import { Card, ScoreBar, SkillChip, MatchGauge } from "../components/ui";
import type { Position } from "../types";

const STEP_LABELS = [
  "Extracting text...",
  "Cleaning text...",
  "TF-IDF representation...",
  "Reducing dimensions...",
  "Calculating similarity...",
  "Generating score...",
];

export default function ResumeScreeningPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [positionId, setPositionId] = useState<number | "">("");
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [step, setStep] = useState(-1);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState("");
  const stepTimer = useRef<number | null>(null);

  useEffect(() => {
    api.get("/positions").then((r) => setPositions(r.data.positions));
    return () => { if (stepTimer.current) window.clearInterval(stepTimer.current); };
  }, []);

  function pickFile(f: File) {
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF resumes are supported.");
      return;
    }
    setError("");
    setFile(f);
    setAnalysis(null);
  }

  async function runAnalysis() {
    if (!file) return;
    setError("");
    setAnalysis(null);
    setStep(0);

    stepTimer.current = window.setInterval(() => {
      setStep((s) => (s < STEP_LABELS.length - 1 ? s + 1 : s));
    }, 450);

    const formData = new FormData();
    formData.append("resume", file);
    if (positionId) formData.append("position_id", String(positionId));

    try {
      const res = await api.post("/screening/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTimeout(() => {
        if (stepTimer.current) window.clearInterval(stepTimer.current);
        setStep(STEP_LABELS.length);
        setAnalysis(res.data.analysis);
      }, STEP_LABELS.length * 450);
    } catch (err: any) {
      if (stepTimer.current) window.clearInterval(stepTimer.current);
      setStep(-1);
      setError(err?.response?.data?.message ?? "Could not analyze this resume.");
    }
  }

  return (
    <div className="space-y-5">
      <Card>
        <h3 className="font-display font-semibold mb-4">Upload a resume</h3>
        <div className="mb-4">
          <label className="text-xs text-slate-500 mb-1 block">Score against position (optional)</label>
          <select
            value={positionId}
            onChange={(e) => setPositionId(e.target.value ? Number(e.target.value) : "")}
            className="w-full md:w-80 px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
          >
            <option value="">Category prediction only</option>
            {positions.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) pickFile(e.dataTransfer.files[0]); }}
          className={`rounded-xl border-2 border-dashed p-10 text-center transition ${
            dragOver ? "border-accent-blue bg-blue-50/40" : "border-slate-200"
          }`}
        >
          <UploadCloud size={28} className="mx-auto text-slate-400 mb-3" />
          <p className="text-sm text-slate-500 mb-1">Drag and drop a PDF resume here</p>
          <p className="text-xs text-slate-400 mb-3">or</p>
          <label className="inline-block bg-navy text-white text-sm px-4 py-2 rounded-lg cursor-pointer hover:bg-navy-light">
            Browse files
            <input type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && pickFile(e.target.files[0])} />
          </label>
          {file && (
            <p className="text-xs text-slate-500 mt-4 flex items-center justify-center gap-1.5">
              <FileText size={14} /> {file.name}
            </p>
          )}
        </div>

        {error && <p className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg mt-4">{error}</p>}

        <button
          onClick={runAnalysis} disabled={!file || step >= 0}
          className="mt-4 w-full md:w-auto bg-accent-blue text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-600 transition disabled:opacity-50"
        >
          Analyze resume
        </button>
      </Card>

      {step >= 0 && (
        <Card>
          <h3 className="font-display font-semibold mb-4">Processing</h3>
          <div className="space-y-3">
            {STEP_LABELS.map((label, i) => (
              <div key={label} className="flex items-center gap-3 text-sm">
                {i < step ? (
                  <CheckCircle2 size={16} className="text-accent-teal shrink-0" />
                ) : i === step ? (
                  <span className="w-4 h-4 rounded-full border-2 border-accent-blue border-t-transparent animate-spin shrink-0" />
                ) : (
                  <span className="w-4 h-4 rounded-full border-2 border-slate-200 shrink-0" />
                )}
                <span className={i <= step ? "text-navy" : "text-slate-400"}>{label}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {analysis && (
        <div className="grid md:grid-cols-2 gap-5">
          <Card>
            <h3 className="font-display font-semibold mb-3">Predicted category</h3>
            <p className="text-2xl font-display font-semibold text-navy">{analysis.predicted_category}</p>
            <p className="text-xs text-slate-400 mt-1">{analysis.category_confidence}% confidence · {analysis.category_mode} mode</p>
          </Card>
          {"overall_match" in analysis && (
            <>
              <Card className="flex flex-col items-center justify-center">
                <MatchGauge score={analysis.overall_match} />
              </Card>
              <Card className="md:col-span-2 space-y-4">
                <h3 className="font-display font-semibold">Score breakdown</h3>
                <ScoreBar label="Skill match" value={analysis.skill_score} />
                <ScoreBar label="Experience fit" value={analysis.experience_score} />
                <ScoreBar label="Education fit" value={analysis.education_score} />
                <ScoreBar label="Keyword overlap" value={analysis.keyword_score} />
              </Card>
              <Card className="md:col-span-2">
                <h3 className="font-display font-semibold mb-3">Matched vs missing skills</h3>
                <div className="flex flex-wrap gap-2">
                  {(analysis.matched_skills ?? []).map((s: string) => <SkillChip key={s} label={s} matched />)}
                  {(analysis.missing_skills ?? []).map((s: string) => <SkillChip key={s} label={s} matched={false} />)}
                </div>
              </Card>
            </>
          )}
        </div>
      )}
    </div>
  );
}
