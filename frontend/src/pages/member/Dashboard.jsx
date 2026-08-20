import { useEffect, useState } from "react";
import api from "../../api";
import StatCard from "../../components/StatCard";
import { useAuth } from "../../context/AuthContext";

const money = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
const sp = (n) => `${Number(n || 0).toFixed(2)} SP`;

export default function Dashboard() {
  const { auth } = useAuth();
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");

  const load = () => api.get("/member/dashboard").then((r) => setD(r.data)).catch(() => setErr("Could not load dashboard"));
  useEffect(() => { load(); }, []);

  const runMatching = async () => {
    await api.post("/member/matching/run");
    load();
  };

  if (err) return <div className="card p-6 text-red-600">{err}</div>;
  if (!d) return <div className="card p-6 text-herb-400">Loading dashboard…</div>;

  return (
    <div className="space-y-6">
      <div className="card overflow-hidden">
        <div className="hero-gradient px-6 py-6 text-white">
          <div className="text-sm text-herb-100">Welcome back,</div>
          <h1 className="text-2xl font-extrabold">{auth?.name} 🌿</h1>
          <div className="mt-1 text-xs text-herb-200">Member ID · {auth?.member_id}</div>
        </div>
        <div className="grid grid-cols-2 gap-4 p-6 sm:grid-cols-3">
          <StatCard label="This Week Payout" value={money(d.week_payout)} accent="marigold" icon="💵" />
          <StatCard label="Total Payout" value={money(d.total_payout)} accent="marigold" icon="🏦" />
          <StatCard label="Wallet Balance" value={money(d.wallet_balance)} accent="marigold" icon="👛" />
        </div>
      </div>

      <div>
        <h2 className="mb-3 text-lg font-bold text-herb-800">Business Volume</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          <StatCard label="Left Selling Points" value={sp(d.left_sp)} icon="⬅️" />
          <StatCard label="Right Selling Points" value={sp(d.right_sp)} icon="➡️" />
          <StatCard label="Matching SP" value={sp(d.matching_sp)} accent="marigold" icon="⚖️" />
          <StatCard label="Self Purchase" value={sp(d.self_purchase)} icon="🛍️" />
          <StatCard label="Left Carry Forward" value={sp(d.left_carry)} icon="🔁" />
          <StatCard label="Right Carry Forward" value={sp(d.right_carry)} icon="🔁" />
          <StatCard label="Total Left SP" value={sp(d.total_left_sp)} icon="📊" />
          <StatCard label="Total Right SP" value={sp(d.total_right_sp)} icon="📊" />
        </div>
      </div>

      <div>
        <h2 className="mb-3 text-lg font-bold text-herb-800">Bonuses</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <StatCard label="Level Bonus" value={money(d.level_bonus)} accent="marigold" icon="🏆" />
          <StatCard label="Level Bonus Received" value={money(d.level_bonus_received)} accent="marigold" icon="✅" />
          <StatCard label="Capping Limit" value={money(d.capping_limit)} icon="🛡️" />
        </div>
      </div>

      <div className="card flex flex-wrap items-center justify-between gap-3 p-5">
        <div>
          <div className="font-semibold text-herb-800">Run binary matching</div>
          <div className="text-sm text-herb-500">Match your left & right carry-forward SP and credit the bonus to your wallet.</div>
        </div>
        <button onClick={runMatching} className="btn-primary">Calculate Matching</button>
      </div>
    </div>
  );
}
