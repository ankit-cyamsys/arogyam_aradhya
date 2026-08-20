import { useEffect, useState } from "react";
import api from "../../api";
import StatCard from "../../components/StatCard";

export default function Overview() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/admin/overview").then((r) => setD(r.data)).catch(() => {}); }, []);
  if (!d) return <div className="text-herb-400">Loading…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">Dashboard Overview</h1>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard label="Total Members" value={d.members} icon="👥" />
        <StatCard label="Active Members" value={d.active_members} accent="marigold" icon="✅" />
        <StatCard label="Orders" value={d.orders} icon="📦" />
        <StatCard label="Revenue" value={`₹${Number(d.revenue).toLocaleString("en-IN")}`} accent="marigold" icon="💰" />
        <StatCard label="Pending Payouts" value={d.pending_payouts} icon="⏳" />
      </div>
      <div className="card p-6 text-sm text-herb-600">
        <h2 className="mb-2 font-bold text-herb-800">Welcome, Administrator 🌿</h2>
        <p>Use the sidebar to manage products, members, approve payouts and tune the MLM commission plan. All commission rates are configurable under <b>MLM Settings</b>.</p>
      </div>
    </div>
  );
}
