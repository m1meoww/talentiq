import React, { useState } from "react";
import { Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function SettingsPage() {
  const { user } = useAuth();
  const [semanticWeight, setSemanticWeight] = useState(40);
  const [skillWeight, setSkillWeight] = useState(30);

  return (
    <div className="grid md:grid-cols-2 gap-5">
      <Card>
        <h3 className="font-display font-semibold mb-3">Account</h3>
        <p className="text-sm text-slate-500 mb-1"><b>Name:</b> {user?.name}</p>
        <p className="text-sm text-slate-500 mb-1"><b>Email:</b> {user?.email}</p>
        <p className="text-sm text-slate-500"><b>Role:</b> {user?.role}</p>
      </Card>

      <Card>
        <h3 className="font-display font-semibold mb-3">ML scoring weights</h3>
        <p className="text-xs text-slate-400 mb-4">
          Adjust how much semantic similarity vs. exact skill overlap contributes
          to the overall match score. (Demo control — wire to backend WEIGHTS config to persist.)
        </p>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>Semantic similarity</span><span>{semanticWeight}%</span>
            </div>
            <input type="range" min={0} max={100} value={semanticWeight}
              onChange={(e) => setSemanticWeight(Number(e.target.value))} className="w-full accent-accent-blue" />
          </div>
          <div>
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>Skill overlap</span><span>{skillWeight}%</span>
            </div>
            <input type="range" min={0} max={100} value={skillWeight}
              onChange={(e) => setSkillWeight(Number(e.target.value))} className="w-full accent-accent-teal" />
          </div>
        </div>
      </Card>
    </div>
  );
}
