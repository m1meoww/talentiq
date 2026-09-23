import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, X } from "lucide-react";
import { api } from "../api/client";
import { Card, StatusBadge } from "../components/ui";
import type { Position } from "../types";

function CreatePositionModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({
    title: "", department: "", location: "", requirements: "", preferred_skills: "",
  });
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post("/positions", {
        ...form,
        preferred_skills: form.preferred_skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      onCreated();
      onClose();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-navy/40 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-lg">New position</h3>
          <button onClick={onClose}><X size={18} className="text-slate-400" /></button>
        </div>
        <form onSubmit={submit} className="space-y-3">
          <input required placeholder="Title" value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200" />
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="Department" value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              className="px-3 py-2 text-sm rounded-lg border border-slate-200" />
            <input placeholder="Location" value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="px-3 py-2 text-sm rounded-lg border border-slate-200" />
          </div>
          <textarea placeholder="Requirements" value={form.requirements}
            onChange={(e) => setForm({ ...form, requirements: e.target.value })}
            rows={3} className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200" />
          <input placeholder="Preferred skills (comma-separated)" value={form.preferred_skills}
            onChange={(e) => setForm({ ...form, preferred_skills: e.target.value })}
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200" />
          <button type="submit" disabled={saving}
            className="w-full bg-accent-blue text-white py-2.5 rounded-lg text-sm font-medium disabled:opacity-60">
            {saving ? "Creating..." : "Create position"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function PositionsPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [showModal, setShowModal] = useState(false);

  function load() {
    api.get("/positions").then((r) => setPositions(r.data.positions));
  }

  useEffect(load, []);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">{positions.length} positions</p>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 bg-navy text-white text-sm px-4 py-2 rounded-lg hover:bg-navy-light">
          <Plus size={15} /> New position
        </button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {positions.map((p) => (
          <Link key={p.id} to={`/positions/${p.id}`}>
            <Card className="h-full hover:border-accent-blue/40 transition">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-display font-semibold text-navy">{p.title}</h3>
                <StatusBadge status={p.status} />
              </div>
              <p className="text-xs text-slate-400 mb-4">{p.department} · {p.location}</p>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{p.applicant_count ?? 0} applicants</span>
                <span className="font-medium text-navy">{p.avg_score ?? 0}% avg match</span>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {showModal && <CreatePositionModal onClose={() => setShowModal(false)} onCreated={load} />}
    </div>
  );
}
