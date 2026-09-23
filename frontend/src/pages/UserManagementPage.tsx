import React from "react";
import { Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function UserManagementPage() {
  const { user } = useAuth();

  if (user?.role !== "Admin") {
    return (
      <Card>
        <p className="text-sm text-slate-500">
          User management is only available to Admin accounts. Sign in as an Admin
          (try the demo account on the login screen) to manage roles.
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <h3 className="font-display font-semibold mb-2">Role management</h3>
      <p className="text-sm text-slate-500">
        This is a placeholder for full user administration (list users, change roles,
        deactivate accounts). Wire it up to <code className="text-xs bg-surface px-1.5 py-0.5 rounded">GET/PUT /api/users</code> endpoints
        as your next backend iteration.
      </p>
    </Card>
  );
}
