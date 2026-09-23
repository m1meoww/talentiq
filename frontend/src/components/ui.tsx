import React from "react";

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-card p-5 ${className}`}>
      {children}
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  Applied: "bg-slate-100 text-slate-600",
  "Under Review": "bg-amber-50 text-amber-700",
  Shortlisted: "bg-blue-50 text-accent-blue",
  Interview: "bg-violet-50 text-violet-700",
  Selected: "bg-teal-50 text-accent-teal",
  Rejected: "bg-rose-50 text-rose-600",
  Open: "bg-teal-50 text-accent-teal",
  Closed: "bg-slate-100 text-slate-500",
  "On-Hold": "bg-amber-50 text-amber-700",
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? "bg-slate-100 text-slate-600";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${style}`}>
      {status}
    </span>
  );
}

export function ScoreBar({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "bg-accent-teal" : value >= 45 ? "bg-amber-400" : "bg-rose-400";
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-500 mb-1">
        <span>{label}</span>
        <span className="font-medium text-navy">{value}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  );
}

export function MatchGauge({ score, size = 120 }: { score: number; size?: number }) {
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? "#14B8A6" : score >= 45 ? "#F59E0B" : "#F43F5E";

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#F1F5F9" strokeWidth={10} fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={radius} stroke={color} strokeWidth={10} fill="none"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display font-semibold text-2xl text-navy">{Math.round(score)}%</span>
        <span className="text-[11px] text-slate-400">Match</span>
      </div>
    </div>
  );
}

export function SkillChip({ label, matched }: { label: string; matched: boolean }) {
  return (
    <span
      className={`px-2.5 py-1 rounded-full text-xs font-medium ${
        matched ? "bg-teal-50 text-accent-teal" : "bg-rose-50 text-rose-500"
      }`}
    >
      {label}
    </span>
  );
}

export function KPICard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <Card>
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="font-display font-semibold text-2xl text-navy">{value}</p>
      {hint && <p className="text-[11px] text-accent-teal mt-1">{hint}</p>}
    </Card>
  );
}
