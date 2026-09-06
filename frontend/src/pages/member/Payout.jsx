import { useEffect, useState } from "react";
import api from "../../api";

const sp = (n) => Number(n || 0).toFixed(2);
const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Payout() {
  const [reg, setReg] = useState(null);
  const [me, setMe] = useState(null);
  const [amount, setAmount] = useState("");
  const [msg, setMsg] = useState(null);
  const [showWithdraw, setShowWithdraw] = useState(false);

  const load = () => {
    api.get("/member/payout-register").then((r) => setReg(r.data)).catch(() => setReg({ total_earned: 0, rows: [] }));
    api.get("/member/me").then((r) => setMe(r.data)).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const withdraw = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      await api.post("/mlm/payouts", { amount: Number(amount) });
      setAmount(""); setMsg({ ok: true, text: "Withdrawal request submitted!" }); load();
    } catch (err) {
      setMsg({ ok: false, text: err.friendlyMessage || err.response?.data?.detail || "Request failed" });
    }
  };

  if (!reg) return <div className="card p-6 text-herb-400">Loading payout register…</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-herb-800">Payout</h1>
        <button onClick={() => setShowWithdraw(!showWithdraw)} className="btn-outline py-2">
          {showWithdraw ? "Hide" : "Request Withdrawal"}
        </button>
      </div>

      <div className="card p-6 text-center">
        <div className="text-xs uppercase tracking-wide text-herb-500">Total Payout Earned</div>
        <div className="mt-1 text-4xl font-extrabold text-marigold-600">{inr(reg.total_earned)}</div>
        <div className="mt-1 text-sm text-herb-500">Wallet balance: {inr(me?.wallet_balance)}</div>
      </div>

      {showWithdraw && (
        <form onSubmit={withdraw} className="card flex flex-wrap items-end gap-3 p-5">
          <div className="flex-1">
            <label className="label">Withdraw Amount (₹)</label>
            <input className="input" type="number" min="1" value={amount} onChange={(e) => setAmount(e.target.value)} required />
          </div>
          <button className="btn-primary">Submit Request</button>
          {msg && <div className={`w-full rounded-xl px-4 py-2 text-sm ${msg.ok ? "bg-herb-50 text-herb-700" : "bg-red-50 text-red-700"}`}>{msg.text}</div>}
        </form>
      )}

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr>
              <th className="px-3 py-3">Week</th>
              <th className="px-3 py-3 text-right">Left SP</th>
              <th className="px-3 py-3 text-right">Right SP</th>
              <th className="px-3 py-3 text-right">Matching SP</th>
              <th className="px-3 py-3 text-right">Closing SP</th>
              <th className="px-3 py-3 text-right">Payout</th>
              <th className="px-3 py-3 text-right">CF Left</th>
              <th className="px-3 py-3 text-right">CF Right</th>
              <th className="px-3 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {reg.rows.map((r, i) => (
              <tr key={i}>
                <td className="px-3 py-2.5 font-medium text-herb-800">{r.week_label}</td>
                <td className="px-3 py-2.5 text-right">{sp(r.left_sp)}</td>
                <td className="px-3 py-2.5 text-right">{sp(r.right_sp)}</td>
                <td className="px-3 py-2.5 text-right">{sp(r.matching_sp)}</td>
                <td className="px-3 py-2.5 text-right font-semibold">{sp(r.closing_sp)}</td>
                <td className="px-3 py-2.5 text-right font-bold text-herb-700">{inr(r.payout)}</td>
                <td className="px-3 py-2.5 text-right text-herb-500">{sp(r.cf_left)}</td>
                <td className="px-3 py-2.5 text-right text-herb-500">{sp(r.cf_right)}</td>
                <td className="px-3 py-2.5"><span className="chip bg-herb-100 text-herb-700">✓ {r.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
        {reg.rows.length === 0 && <div className="p-8 text-center text-herb-400">No payouts yet. Matching is settled weekly.</div>}
      </div>
    </div>
  );
}
