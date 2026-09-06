import { useEffect, useState } from "react";
import api from "../../api";
import StatCard from "../../components/StatCard";

const sp = (n) => `${Number(n || 0).toFixed(2)} SP`;
const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function LevelBonus() {
  const [d, setD] = useState(null);
  useEffect(() => {
    api.get("/member/level-bonus").then((r) => setD(r.data)).catch(() => {});
  }, []);
  if (!d) return <div className="card p-6 text-herb-400">Loading…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">Level Bonus</h1>

      <div className="card overflow-hidden">
        <div className="hero-gradient flex items-center justify-between px-6 py-5 text-white">
          <div>
            <div className="text-xs text-herb-100">Current Rank</div>
            <div className="text-2xl font-extrabold">🏆 {d.level_name}</div>
          </div>
          <span className="chip bg-white/15 text-white ring-1 ring-white/25">{d.tier} · Level {d.stored_level}</span>
        </div>
        <div className="grid grid-cols-1 gap-4 p-6 sm:grid-cols-3">
          <StatCard label="Cumulative Left SP" value={sp(d.cumulative_left_sp)} icon="⬅️" />
          <StatCard label="Cumulative Right SP" value={sp(d.cumulative_right_sp)} icon="➡️" />
          <StatCard label="Matching SP" value={sp(d.matching_sp)} accent="marigold" icon="⚖️" />
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="border-b border-herb-100 px-6 py-3 font-bold text-herb-800">Bonus Payments</div>
        {d.bonus_payments.length === 0 ? (
          <div className="p-8 text-center text-herb-400">No rank bonus paid yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
              <tr><th className="px-4 py-3">Date</th><th className="px-4 py-3">Detail</th><th className="px-4 py-3 text-right">Amount</th><th className="px-4 py-3">Status</th></tr>
            </thead>
            <tbody className="divide-y divide-herb-50">
              {d.bonus_payments.map((p, i) => (
                <tr key={i}>
                  <td className="px-4 py-3 text-herb-500">{new Date(p.date).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-herb-700">{p.remarks || "Rank bonus"}</td>
                  <td className="px-4 py-3 text-right font-semibold text-herb-700">{inr(p.amount)}</td>
                  <td className="px-4 py-3"><span className="chip bg-herb-100 text-herb-700 capitalize">{p.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card overflow-x-auto">
        <div className="border-b border-herb-100 px-6 py-3 font-bold text-herb-800">Career Path & Rank Rewards</div>
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr><th className="px-4 py-3">Rank</th><th className="px-4 py-3 text-right">SP (each leg)</th><th className="px-4 py-3 text-right">Bonus</th><th className="px-4 py-3">Reward</th></tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {d.ranks.map((r) => (
              <tr key={r.level} className={r.level === d.stored_level ? "bg-marigold-50" : ""}>
                <td className="px-4 py-2.5 font-semibold text-herb-800">{r.level}. {r.name}</td>
                <td className="px-4 py-2.5 text-right">{Number(r.sp).toLocaleString("en-IN")}</td>
                <td className="px-4 py-2.5 text-right font-semibold text-marigold-600">{inr(r.bonus)}</td>
                <td className="px-4 py-2.5 text-herb-600">{r.reward}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
