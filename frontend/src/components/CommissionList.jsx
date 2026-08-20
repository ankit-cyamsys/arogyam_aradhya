import { useEffect, useState } from "react";
import api from "../api";

export default function CommissionList({ kind, title, emptyText }) {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    api
      .get("/mlm/commissions", { params: { kind } })
      .then((r) => setRows(r.data))
      .catch(() => setRows([]));
  }, [kind]);

  const total = (rows || []).reduce((s, r) => s + Number(r.amount), 0);

  if (!rows) return <div className="card p-6 text-herb-400">Loading…</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <h1 className="text-2xl font-extrabold text-herb-800">{title}</h1>
        <div className="text-right">
          <div className="text-xs uppercase text-herb-500">Total earned</div>
          <div className="text-xl font-extrabold text-marigold-600">₹{total.toFixed(2)}</div>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="card p-10 text-center text-herb-500">{emptyText}</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Detail</th>
                <th className="px-4 py-3 text-right">SP</th>
                <th className="px-4 py-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-herb-50">
              {rows.map((r) => (
                <tr key={r.id}>
                  <td className="px-4 py-3 text-herb-500">{new Date(r.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-herb-700">{r.note || r.kind}</td>
                  <td className="px-4 py-3 text-right text-herb-500">{r.sp_matched || "—"}</td>
                  <td className="px-4 py-3 text-right font-semibold text-herb-700">₹{Number(r.amount).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
