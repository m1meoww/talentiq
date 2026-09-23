import React, { useEffect, useState } from "react";
import { FileDown } from "lucide-react";
import { api } from "../api/client";
import { Card } from "../components/ui";
import type { Position } from "../types";

export default function ReportsPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [candidateId, setCandidateId] = useState("");

  useEffect(() => {
    api.get("/positions").then((r) => setPositions(r.data.positions));
  }, []);

  function download(url: string) {
    window.open(url, "_blank");
  }

  return (
    <div className="grid md:grid-cols-3 gap-5">
      <Card>
        <FileDown size={20} className="text-accent-blue mb-3" />
        <h3 className="font-display font-semibold mb-2">Position applicant report</h3>
        <p className="text-sm text-slate-500 mb-4">All applicants for a position, ranked by match score.</p>
        <select id="pos-select" className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 mb-3">
          {positions.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        <button
          onClick={() => {
            const sel = document.getElementById("pos-select") as HTMLSelectElement;
            download(`/api/reports/position/${sel.value}`);
          }}
          className="w-full bg-navy text-white py-2.5 rounded-lg text-sm font-medium hover:bg-navy-light"
        >
          Download PDF
        </button>
      </Card>

      <Card>
        <FileDown size={20} className="text-accent-teal mb-3" />
        <h3 className="font-display font-semibold mb-2">Candidate screening report</h3>
        <p className="text-sm text-slate-500 mb-4">Full profile and score breakdown for one candidate.</p>
        <input
          value={candidateId} onChange={(e) => setCandidateId(e.target.value)}
          placeholder="Candidate ID"
          className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 mb-3"
        />
        <button
          onClick={() => candidateId && download(`/api/reports/candidate/${candidateId}`)}
          className="w-full bg-navy text-white py-2.5 rounded-lg text-sm font-medium hover:bg-navy-light"
        >
          Download PDF
        </button>
      </Card>

      <Card>
        <FileDown size={20} className="text-violet-500 mb-3" />
        <h3 className="font-display font-semibold mb-2">Recruitment analytics report</h3>
        <p className="text-sm text-slate-500 mb-4">A snapshot of key hiring metrics across the pipeline.</p>
        <button
          onClick={() => download("/api/reports/analytics")}
          className="w-full bg-navy text-white py-2.5 rounded-lg text-sm font-medium hover:bg-navy-light mt-[3.25rem]"
        >
          Download PDF
        </button>
      </Card>
    </div>
  );
}
