import React from "react";
import { useLocation } from "react-router-dom";
import { Search, Bell } from "lucide-react";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/candidates": "Candidates",
  "/positions": "Positions",
  "/screening": "Resume Screening",
  "/applications": "Applications",
  "/assistant": "Talia Assistant",
  "/analytics": "Analytics",
  "/reports": "Reports",
  "/users": "User Management",
  "/settings": "Settings",
};

export default function Header() {
  const location = useLocation();
  const base = "/" + location.pathname.split("/")[1];
  const title = TITLES[base] ?? "TalentIQ";

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-white border-b border-slate-200 sticky top-0 z-10">
      <div>
        <p className="text-[12px] text-slate-400">TalentIQ / {title}</p>
        <h1 className="font-display font-semibold text-lg text-navy leading-tight">{title}</h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative hidden sm:block">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            placeholder="Search candidates, positions..."
            className="pl-9 pr-3 py-2 text-sm rounded-lg bg-surface border border-slate-200 w-72 focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
          />
        </div>
        <button className="relative text-slate-500 hover:text-navy">
          <Bell size={19} />
          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-accent-teal" />
        </button>
      </div>
    </header>
  );
}
