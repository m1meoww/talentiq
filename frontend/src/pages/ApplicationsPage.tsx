import React, { useEffect, useState } from "react";
import { X, History } from "lucide-react";
import { api } from "../api/client";
import { Card, StatusBadge } from "../components/ui";
import type { Application, ApplicationHistoryEntry } from "../types";

const STATUSES = ["Applied", "Under Review", "Shortlisted", "Interview", "Selected", "Rejected"];

function HistoryModal({ applicationId, onClose }: { applicationId: number; onClose: () => void }) {
  const [history, setHistory] = useState<ApplicationHistoryEntry[]>([]);

  useEffect(() => {
    api.get(`/applications/${applicationId}/history`).then((r) => setHistory(r.data.history));
  }, [applicationId]);

  return (
    <div className="fixed inset-0 bg-navy/40 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-lg">Audit history</h3>
          <button onClick={onClose}><X size={18} className="text-slate-400" /></button>
        </div>
        <div className="space-y-4 max-h-96 overflow-y-auto scrollbar-thin">
          {history.map((h) => (
            <div key={h.id} className="flex gap-3">
              <div className="w-2 h-2 rounded-full bg-accent-blue mt-1.5 shrink-0" />
              <div>
                <p className="text-sm text-navy">
                  {h.old_status ? `${h.old_status} → ${h.new_status}` : `Application created (${h.new_status})`}
                </p>
                <p className="text-xs text-slate-400">{h.changed_by} · {new Date(h.changed_at).toLocaleString()}</p>
                {h.remarks && <p className="text-xs text-slate-500 mt-1">{h.remarks}</p>}
              </div>
            </div>
          ))}
          {history.length === 0 && <p className="text-sm text-slate-400">No history yet.</p>}
        </div>
      </div>
    </div>
  );
}

function StatusModal({ app, onClose, onUpdated }: { app: Application; onClose: () => void; onUpdated: () => void }) {
  const [status, setStatus] = useState(app.status);
  const [remarks, setRemarks] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put(`/applications/${app.id}/status`, { status, remarks });
      onUpdated();
      onClose();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-navy/40 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-xl w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-lg">Update status</h3>
          <button onClick={onClose}><X size={18} className="text-slate-400" /></button>
        </div>
        <form onSubmit={submit} className="space-y-3">
          <select value={status} onChange={(e) => setStatus(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white">
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <textarea placeholder="Remarks (optional)" value={remarks} onChange={(e) => setRemarks(e.target.value)}
            rows={3} className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200" />
          <button type="submit" disabled={saving}
            className="w-full bg-accent-blue text-white py-2.5 rounded-lg text-sm font-medium disabled:opacity-60">
            {saving ? "Saving..." : "Save status"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [historyId, setHistoryId] = useState<number | null>(null);
  const [editing, setEditing] = useState<Application | null>(null);

  function load() {
    api.get("/applications", { params: { status: statusFilter || undefined } })
      .then((r) => setApplications(r.data.applications));
  }

  useEffect(load, [statusFilter]);

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white">
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <p className="text-xs text-slate-400">{applications.length} applications</p>
      </div>

      <Card className="p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface">
            <tr className="text-left text-slate-400 text-xs">
              <th className="px-5 py-3 font-medium">Candidate</th>
              <th className="px-5 py-3 font-medium">Position</th>
              <th className="px-5 py-3 font-medium">Match</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {applications.map((a) => (
              <tr key={a.id} className="border-t border-slate-100">
                <td className="px-5 py-3">{a.candidate_name}</td>
                <td className="px-5 py-3 text-slate-500">{a.position_title}</td>
                <td className="px-5 py-3 font-medium text-navy">{a.match_score}%</td>
                <td className="px-5 py-3">
                  <button onClick={() => setEditing(a)}>
                    <StatusBadge status={a.status} />
                  </button>
                </td>
                <td className="px-5 py-3 text-right">
                  <button onClick={() => setHistoryId(a.id)} className="text-slate-400 hover:text-accent-blue">
                    <History size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {historyId && <HistoryModal applicationId={historyId} onClose={() => setHistoryId(null)} />}
      {editing && <StatusModal app={editing} onClose={() => setEditing(null)} onUpdated={load} />}
    </div>
  );
}
