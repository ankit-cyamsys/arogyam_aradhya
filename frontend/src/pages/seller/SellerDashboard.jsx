import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api";
import StatCard from "../../components/StatCard";
import { useAuth } from "../../context/AuthContext";

const money = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;

export default function SellerDashboard() {
  const { auth } = useAuth();
  const [d, setD] = useState(null);

  useEffect(() => {
    api.get("/member/direct/dashboard").then((r) => setD(r.data)).catch(() => {});
  }, []);

  if (!d) return <div className="card p-6 text-herb-400">Loading dashboard…</div>;

  return (
    <div className="space-y-6">
      <div className="card overflow-hidden">
        <div className="bg-gradient-to-br from-marigold-500 to-marigold-700 px-6 py-6 text-white">
          <div className="text-sm text-marigold-100">Welcome back,</div>
          <h1 className="text-2xl font-extrabold">{auth?.name} 🛍️</h1>
          <div className="mt-1 text-xs text-marigold-100">Seller ID · {auth?.member_id} · Commission {d.dsa_percent}%</div>
        </div>
        <div className="grid grid-cols-2 gap-4 p-6 sm:grid-cols-4">
          <StatCard label="Total Sales" value={money(d.total_sales)} icon="🧾" />
          <StatCard label="Total Earnings" value={money(d.dsa_earned)} accent="marigold" icon="💰" />
          <StatCard label="Wallet Balance" value={money(d.wallet_balance)} accent="marigold" icon="👛" />
          <StatCard label="Orders" value={d.order_count} icon="📦" />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Paid Out" value={money(d.total_paid)} icon="🏦" />
        <StatCard label="Business Volume" value={`${Number(d.total_sp).toFixed(2)} SP`} icon="📊" />
        <StatCard label="Commission Rate" value={`${d.dsa_percent}%`} accent="marigold" icon="⚡" />
      </div>

      <div className="card flex flex-wrap items-center justify-between gap-3 p-6">
        <div>
          <div className="font-bold text-herb-800">Ready to earn more?</div>
          <div className="text-sm text-herb-500">Every product you sell credits {d.dsa_percent}% to your wallet instantly.</div>
        </div>
        <Link to="/products" className="btn-accent">Browse & Sell Products →</Link>
      </div>
    </div>
  );
}
