import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Users, Briefcase, ScanSearch, ClipboardList,
  BarChart3, MessageSquareText, FileOutput, ShieldCheck, Settings, LogOut,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const mainLinks = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/candidates", label: "Candidates", icon: Users },
  { to: "/positions", label: "Positions", icon: Briefcase },
  { to: "/screening", label: "Resume Screening", icon: ScanSearch },
  { to: "/applications", label: "Applications", icon: ClipboardList },
  { to: "/assistant", label: "Talia Assistant", icon: MessageSquareText },
];

const analyticsLinks = [
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileOutput },
];

const systemLinks = [
  { to: "/users", label: "User Management", icon: ShieldCheck },
  { to: "/settings", label: "Settings", icon: Settings },
];

function Section({ title, links }: { title: string; links: typeof mainLinks }) {
  return (
    <div className="mb-6">
      <p className="px-3 mb-2 text-[11px] tracking-wide text-white/40 font-medium">{title}</p>
      <nav className="space-y-0.5">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-accent-blue/20 text-white font-medium"
                  : "text-white/65 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            <Icon size={17} strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 bg-navy flex flex-col">
      <div className="px-5 py-6 flex items-center gap-2 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-accent-teal flex items-center justify-center font-display font-bold text-navy">
          T
        </div>
        <div>
          <p className="font-display font-semibold text-white leading-tight">TalentIQ</p>
          <p className="text-[11px] text-white/40 leading-tight">Recruitment Intelligence</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-5 scrollbar-thin">
        <Section title="MAIN" links={mainLinks} />
        <Section title="ANALYTICS" links={analyticsLinks} />
        <Section title="SYSTEM" links={systemLinks} />
      </div>

      <div className="px-4 py-4 border-t border-white/10 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-accent-blue/30 flex items-center justify-center text-white text-sm font-semibold">
          {user?.name?.[0]?.toUpperCase() ?? "U"}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-white truncate">{user?.name}</p>
          <p className="text-[11px] text-white/40">{user?.role}</p>
        </div>
        <button onClick={logout} title="Log out" className="text-white/50 hover:text-white">
          <LogOut size={17} />
        </button>
      </div>
    </aside>
  );
}
