import { useEffect, useState } from "react";
import api from "../../api";

export default function Payout() {
  const [me, setMe] = useState(null);
  const [rows, setRows] = useState([]);
  const [amount, setAmount] = useState("");
  const [msg, setMsg] = useState(null);

  const load = () => {
    api.get("/member/me").then((r) => setMe(r.data));
    api.get("/mlm/payouts").then((r) => setRows(r.data));
  };
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      await api.post("/mlm/payouts", { amount: Number(amount) });
      setAmount("");
      setMsg({ ok: true, text: "Payout request submitted!" });
      load();
    } catch (err) {
      setMsg({ ok: false, text: err.response?.data?.detail || "Request failed" });
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">Payout</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-6">
          <div className="text-xs uppercase text-herb-500">Available Wallet Balance</div>
          <div className="mt-1 text-3xl font-extrabold text-marigold-600">
            ₹{Number(me?.wallet_balance || 0).toFixed(2)}
          </div>
          <form onSubmit={submit} className="mt-5 space-y-3">
            <div>
              <label className="label">Withdraw Amount (₹)</label>
              <input
                className="input"
                type="number"
                min="1"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
            <button className="btn-primary w-full">Request Payout</button>
            {msg && (
              <div className={`rounded-xl px-4 py-2 text-sm ${msg.ok ? "bg-herb-50 text-herb-700" : "bg-red-50 text-red-700"}`}>
                {msg.text}
              </div>
            )}
          </form>
        </div>

        <div className="card p-6 lg:col-span-2">
          <h2 className="mb-4 font-bold text-herb-800">Payout History</h2>
          {rows.length === 0 ? (
            <p className="py-8 text-center text-herb-400">No payout requests yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-xs uppercase text-herb-500">
                <tr><th className="py-2">Date</th><th>Amount</th><th>Status</th></tr>
              </thead>
              <tbody className="divide-y divide-herb-50">
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td className="py-2.5 text-herb-500">{new Date(r.created_at).toLocaleDateString()}</td>
                    <td className="font-semibold text-herb-700">₹{Number(r.amount).toFixed(2)}</td>
                    <td>
                      <span className={`chip ${
                        r.status === "paid" ? "bg-herb-100 text-herb-700"
                        : r.status === "rejected" ? "bg-red-50 text-red-600"
                        : "bg-marigold-50 text-marigold-700"
                      } capitalize`}>{r.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
