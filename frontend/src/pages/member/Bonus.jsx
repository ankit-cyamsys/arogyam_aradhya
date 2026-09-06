import { useEffect, useState } from "react";
import api from "../../api";

const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Bonus() {
  const [rows, setRows] = useState(null);
  useEffect(() => {
    api.get("/member/bonus").then((r) => setRows(r.data)).catch(() => setRows([]));
  }, []);
  if (!rows) return <div className="card p-6 text-herb-400">Loading…</div>;
  const total = rows.reduce((s, r) => s + Number(r.amount), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-herb-800">Bonus Payments</h1>
          <p className="text-herb-500">All your rank & referral bonus payments</p>
        </div>
        <div className="text-right">
          <div className="text-xs uppercase text-herb-500">Total</div>
          <div className="text-xl font-extrabold text-marigold-600">{inr(total)}</div>
        </div>
      </div>

      <div className="card overflow-x-auto">
        {rows.length === 0 ? (
          <div className="p-8 text-center text-herb-400">No bonus payments yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
              <tr><th className="px-4 py-3">S.No</th><th className="px-4 py-3">Payment Date</th><th className="px-4 py-3">Type</th><th className="px-4 py-3 text-right">Amount</th><th className="px-4 py-3">Status</th></tr>
            </thead>
            <tbody className="divide-y divide-herb-50">
              {rows.map((r, i) => (
                <tr key={i}>
                  <td className="px-4 py-3 text-herb-500">{i + 1}</td>
                  <td className="px-4 py-3 text-herb-700">{new Date(r.date).toLocaleDateString()}</td>
                  <td className="px-4 py-3"><span className="chip bg-herb-50 text-herb-700 capitalize">{r.kind}</span></td>
                  <td className="px-4 py-3 text-right font-semibold text-herb-700">{inr(r.amount)}</td>
                  <td className="px-4 py-3"><span className="chip bg-herb-100 text-herb-700 uppercase">{r.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
