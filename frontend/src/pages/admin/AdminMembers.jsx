import { useEffect, useState } from "react";
import api from "../../api";

export default function AdminMembers() {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");

  const load = () => api.get("/admin/members", { params: { q: q || undefined } }).then((r) => setRows(r.data));
  useEffect(() => { load(); }, [q]);

  const toggle = async (id) => { await api.post(`/admin/members/${id}/block`); load(); };
  const payRank = async (id) => {
    const { data } = await api.post(`/admin/members/${id}/pay-rank-bonus`);
    if (data.paid.length === 0) alert("No pending rank bonus for this member.");
    else alert("Paid rank bonuses: " + data.paid.map((p) => `${p.name} ₹${p.bonus}`).join(", "));
    load();
  };
  const RANK_NAMES = ["—","Winner","Achiever","Warrior","Champion","Master","Commander","Royal Exec","Imperial","Diamond","Crown","King","Global Icon"];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-herb-800">Members</h1>
        <input className="input max-w-xs" placeholder="Search name / ID…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr><th className="px-4 py-3">Member ID</th><th className="px-4 py-3">Portal</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Rank</th><th className="px-4 py-3">Wallet</th><th className="px-4 py-3">Earned</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Actions</th></tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {rows.map((m) => (
              <tr key={m.member_id}>
                <td className="px-4 py-3 font-semibold text-marigold-600">{m.member_id}</td>
                <td className="px-4 py-3">
                  <span className={`chip ${m.segment === "direct" ? "bg-marigold-50 text-marigold-700" : "bg-herb-50 text-herb-700"}`}>
                    {m.segment === "direct" ? "Direct" : "MLM"}
                  </span>
                </td>
                <td className="px-4 py-3 text-herb-800">{m.name}</td>
                <td className="px-4 py-3">
                  {m.segment === "mlm" && m.rank_level > 0
                    ? <span className="chip bg-herb-50 text-herb-700">{RANK_NAMES[m.rank_level]}</span>
                    : <span className="text-herb-300">—</span>}
                </td>
                <td className="px-4 py-3">₹{Number(m.wallet_balance).toFixed(2)}</td>
                <td className="px-4 py-3">₹{Number(m.total_earned).toFixed(2)}</td>
                <td className="px-4 py-3">
                  {m.is_blocked
                    ? <span className="chip bg-red-50 text-red-600">Blocked</span>
                    : <span className={`chip ${m.is_active ? "bg-herb-100 text-herb-700" : "bg-slate-100 text-slate-500"}`}>{m.is_active ? "Active" : "Inactive"}</span>}
                </td>
                <td className="px-4 py-3 text-right">
                  {m.segment === "mlm" && m.rank_level > m.rank_bonus_paid_level && (
                    <button onClick={() => payRank(m.member_id)} className="mr-2 font-semibold text-marigold-600 hover:underline">Pay Rank Bonus</button>
                  )}
                  <button onClick={() => toggle(m.member_id)} className={m.is_blocked ? "text-herb-600 hover:underline" : "text-red-500 hover:underline"}>
                    {m.is_blocked ? "Unblock" : "Block"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <div className="p-8 text-center text-herb-400">No members found.</div>}
      </div>
    </div>
  );
}
