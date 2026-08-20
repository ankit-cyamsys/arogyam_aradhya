import { useEffect, useState } from "react";
import api from "../../api";

export default function AdminPayouts() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("");

  const load = () => api.get("/admin/payouts", { params: { status: filter || undefined } }).then((r) => setRows(r.data));
  useEffect(() => { load(); }, [filter]);

  const act = async (id, action) => { await api.post(`/admin/payouts/${id}/action`, null, { params: { action } }); load(); };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-herb-800">Payout Requests</h1>
        <div className="flex gap-2">
          {["", "pending", "approved", "paid", "rejected"].map((s) => (
            <button key={s} onClick={() => setFilter(s)}
              className={`chip px-3 py-1.5 capitalize ${filter === s ? "bg-herb-600 text-white" : "bg-white text-herb-600 ring-1 ring-herb-200"}`}>
              {s || "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr><th className="px-4 py-3">Date</th><th className="px-4 py-3">Member</th><th className="px-4 py-3">Amount</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Actions</th></tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-3 text-herb-500">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3"><span className="font-semibold text-herb-800">{r.name}</span> <span className="text-xs text-marigold-600">{r.member_id}</span></td>
                <td className="px-4 py-3 font-bold text-herb-700">₹{Number(r.amount).toFixed(2)}</td>
                <td className="px-4 py-3"><span className="chip bg-herb-50 text-herb-700 capitalize">{r.status}</span></td>
                <td className="px-4 py-3">
                  {r.status === "pending" && <button onClick={() => act(r.id, "approve")} className="mr-2 text-herb-600 hover:underline">Approve</button>}
                  {(r.status === "pending" || r.status === "approved") && <button onClick={() => act(r.id, "pay")} className="mr-2 text-marigold-600 hover:underline">Mark Paid</button>}
                  {r.status !== "paid" && r.status !== "rejected" && <button onClick={() => act(r.id, "reject")} className="text-red-500 hover:underline">Reject</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <div className="p-8 text-center text-herb-400">No payout requests.</div>}
      </div>
    </div>
  );
}
