import { useEffect, useState } from "react";
import api from "../../api";

const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function AdminOrders() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [busy, setBusy] = useState(0);

  const load = () => api.get("/admin/orders", { params: { status: filter || undefined } }).then((r) => setRows(r.data));
  useEffect(() => { load(); }, [filter]);

  const confirm = async (id) => {
    if (!window.confirm("Confirm payment received for this order? This will credit SP & commissions.")) return;
    setBusy(id);
    try { await api.post(`/admin/orders/${id}/confirm`); load(); }
    catch (e) { alert(e.friendlyMessage || e.response?.data?.detail || "Failed"); }
    finally { setBusy(0); }
  };
  const cancel = async (id) => {
    if (!window.confirm("Cancel this order?")) return;
    setBusy(id);
    try { await api.post(`/admin/orders/${id}/cancel`); load(); }
    catch (e) { alert(e.friendlyMessage || e.response?.data?.detail || "Failed"); }
    finally { setBusy(0); }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-herb-800">Orders</h1>
        <div className="flex gap-2">
          {["pending", "paid", "cancelled", ""].map((s) => (
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
            <tr>
              <th className="px-4 py-3">Order</th><th className="px-4 py-3">Member</th>
              <th className="px-4 py-3">Items</th><th className="px-4 py-3 text-right">Total</th>
              <th className="px-4 py-3 text-right">SP</th><th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {rows.map((o) => (
              <tr key={o.id}>
                <td className="px-4 py-3">
                  <div className="font-semibold text-herb-800">{o.order_no}</div>
                  <div className="text-xs text-herb-400">{new Date(o.created_at).toLocaleString()}</div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-herb-800">{o.member_name}</div>
                  <div className="text-xs text-marigold-600">{o.member_id} · {o.segment}</div>
                </td>
                <td className="px-4 py-3 text-xs text-herb-500">
                  {o.items.map((it, i) => <div key={i}>{it.name} × {it.qty}</div>)}
                </td>
                <td className="px-4 py-3 text-right font-bold text-herb-700">{inr(o.total)}</td>
                <td className="px-4 py-3 text-right">{o.total_sp}</td>
                <td className="px-4 py-3">
                  <span className={`chip capitalize ${
                    o.status === "paid" ? "bg-herb-100 text-herb-700"
                    : o.status === "cancelled" ? "bg-red-50 text-red-600"
                    : "bg-marigold-50 text-marigold-700"}`}>{o.status}</span>
                </td>
                <td className="px-4 py-3">
                  {o.payment_status === "unpaid" && o.status !== "cancelled" && (
                    <>
                      <button disabled={busy === o.id} onClick={() => confirm(o.id)} className="mr-2 font-semibold text-herb-600 hover:underline">Confirm Payment</button>
                      <button disabled={busy === o.id} onClick={() => cancel(o.id)} className="text-red-500 hover:underline">Cancel</button>
                    </>
                  )}
                  {o.payment_status === "paid" && <span className="text-xs text-herb-400">✓ confirmed</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <div className="p-8 text-center text-herb-400">No orders.</div>}
      </div>
    </div>
  );
}
