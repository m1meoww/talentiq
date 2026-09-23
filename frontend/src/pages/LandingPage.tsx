import React from "react";
import { Link } from "react-router-dom";
import { ScanSearch, GitCompareArrows, ClipboardCheck, MessageSquareText, BarChart3 } from "lucide-react";

const FEATURES = [
  { icon: ScanSearch, title: "Automated resume intake", body: "PDF parsing with PyMuPDF and pypdf, with clear handling for scanned or invalid files." },
  { icon: GitCompareArrows, title: "Mathematical match scoring", body: "TF-IDF, TruncatedSVD and cosine similarity produce transparent, reproducible match percentages." },
  { icon: ClipboardCheck, title: "Full lifecycle tracking", body: "Every status change is logged to an append-only audit trail, from Applied to Selected." },
  { icon: BarChart3, title: "Recruitment analytics", body: "Trends, funnels and category distributions, updated live as applications move." },
  { icon: MessageSquareText, title: "Talia, the AI assistant", body: "Ask about application status, eligibility or top applicants in plain language." },
];

const STEPS = [
  "Post a position with the skills and experience you need",
  "Candidates upload a resume — text is extracted and cleaned automatically",
  "TalentIQ scores the match against the role using cosine similarity",
  "Recruiters review live rankings and move candidates through the pipeline",
  "Every decision is logged, reported, and available to Talia on request",
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-navy text-white">
      <header className="max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent-teal flex items-center justify-center font-display font-bold text-navy">T</div>
          <span className="font-display font-semibold">TalentIQ</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <Link to="/login" className="text-white/70 hover:text-white">Log in</Link>
          <Link to="/register" className="bg-accent-blue px-4 py-2 rounded-lg font-medium hover:bg-blue-600 transition-colors">
            Try the demo
          </Link>
        </div>
      </header>

      <section className="max-w-6xl mx-auto px-6 pt-16 pb-24 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="text-accent-teal text-sm font-medium mb-3">AI-Powered Recruitment Intelligence</p>
          <h1 className="font-display text-4xl md:text-5xl font-semibold leading-tight mb-5">
            Screen resumes with math, not guesswork.
          </h1>
          <p className="text-white/60 text-lg leading-relaxed mb-8 max-w-md">
            TalentIQ turns every resume into a scored, ranked, auditable candidate —
            using real cosine similarity, not a black box.
          </p>
          <div className="flex gap-3">
            <Link to="/register" className="bg-accent-teal text-navy px-5 py-3 rounded-lg font-semibold hover:opacity-90 transition">
              Get started free
            </Link>
            <Link to="/login" className="border border-white/20 px-5 py-3 rounded-lg font-medium hover:bg-white/5 transition">
              Sign in
            </Link>
          </div>
        </div>

        <div className="bg-navy-light rounded-2xl border border-white/10 p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-white/50">Live match calculation</span>
            <span className="text-xs bg-accent-teal/20 text-accent-teal px-2 py-1 rounded-full">Demo ML mode</span>
          </div>
          {[
            ["Skill overlap", 82],
            ["Semantic similarity", 74],
            ["Experience fit", 90],
            ["Education match", 100],
          ].map(([label, val]) => (
            <div key={label as string} className="mb-3">
              <div className="flex justify-between text-xs text-white/60 mb-1">
                <span>{label}</span><span>{val}%</span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-accent-teal rounded-full" style={{ width: `${val}%` }} />
              </div>
            </div>
          ))}
          <div className="mt-5 pt-4 border-t border-white/10 flex items-center justify-between">
            <span className="text-sm text-white/60">Overall match</span>
            <span className="font-display font-semibold text-2xl text-accent-teal">86.5%</span>
          </div>
        </div>
      </section>

      <section className="bg-surface text-navy py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="font-display text-2xl font-semibold mb-10 text-center">Why TalentIQ</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map(({ icon: Icon, title, body }) => (
              <div key={title} className="bg-white rounded-xl border border-slate-200 p-6 shadow-card">
                <Icon size={22} className="text-accent-blue mb-3" strokeWidth={1.75} />
                <h3 className="font-display font-semibold mb-2">{title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-navy py-20">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="font-display text-2xl font-semibold mb-10 text-center text-white">How it works</h2>
          <ol className="space-y-6">
            {STEPS.map((step, i) => (
              <li key={step} className="flex gap-4">
                <span className="w-8 h-8 rounded-full bg-accent-blue/20 text-accent-blue flex items-center justify-center font-display font-semibold text-sm shrink-0">
                  {i + 1}
                </span>
                <p className="text-white/80 pt-1">{step}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <footer className="text-center text-white/30 text-xs py-8 border-t border-white/10">
        TalentIQ — AI-Powered Recruitment Intelligence
      </footer>
    </div>
  );
}
