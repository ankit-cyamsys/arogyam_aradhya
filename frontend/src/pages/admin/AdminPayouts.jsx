import { useEffect, useState } from "react";
import api from "../../api";

function isoWeek(d = new Date()) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

export default function AdminPayouts() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("");
  const [closing, setClosing] = useState(false);
  const [closeMsg, setCloseMsg] = useState(null);

  const load = () => api.get("/admin/payouts", { params: { status: filter || undefined } }).then((r) => setRows(r.data));
  useEffect(() => { load(); }, [filter]);

  const act = async (id, action) => { await api.post(`/admin/payouts/${id}/action`, null, { params: { action } }); load(); };

  const exportCsv = () => {
    const header = ["Member ID", "Name", "Bank Name", "Bank Account", "IFSC", "Amount", "TDS", "Net", "Status", "Date"];
    const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const lines = [header.map(esc).join(",")];
    rows.forEach((r) => {
      lines.push([
        r.member_id, r.name, r.bank_name, r.bank_account, r.bank_ifsc,
        r.amount, r.tds, r.net, r.status, new Date(r.created_at).toLocaleDateString(),
      ].map(esc).join(","));
    });
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `payouts-${filter || "all"}-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const runClose = async () => {
    const period = isoWeek();
    const label = new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
    if (!confirm(`Run weekly binary-matching close for ${period}?`)) return;
    setClosing(true); setCloseMsg(null);
    try {
      const { data } = await api.post("/admin/payouts/close", null, { params: { period, label } });
      setCloseMsg(`✓ Closed ${data.period}: ${data.rows} members processed, ₹${data.total_paid.toLocaleString("en-IN")} paid.`);
    } catch (e) {
      setCloseMsg("Close failed: " + (e.friendlyMessage || "error"));
    } finally { setClosing(false); }
  };

  return (
    <div className="space-y-6">
      <div className="card flex flex-wrap items-center justify-between gap-3 p-5">
        <div>
          <div className="font-bold text-herb-800">Weekly Matching Close</div>
          <div className="text-sm text-herb-500">Settle binary matching (₹10/SP, blocks of 50) for all members and write the payout register.</div>
          {closeMsg && <div className="mt-2 text-sm font-semibold text-herb-700">{closeMsg}</div>}
        </div>
        <button onClick={runClose} disabled={closing} className="btn-primary">{closing ? "Closing…" : "Run Weekly Close"}</button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-herb-800">Withdrawal Requests</h1>
        <div className="flex flex-wrap items-center gap-2">
          {["", "pending", "approved", "paid", "rejected"].map((s) => (
            <button key={s} onClick={() => setFilter(s)}
              className={`chip px-3 py-1.5 capitalize ${filter === s ? "bg-herb-600 text-white" : "bg-white text-herb-600 ring-1 ring-herb-200"}`}>
              {s || "All"}
            </button>
          ))}
          <button onClick={exportCsv} disabled={rows.length === 0} className="btn-outline py-1.5">⬇ Export to Excel (CSV)</button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr>
              <th className="px-4 py-3">Date</th><th className="px-4 py-3">Member</th>
              <th className="px-4 py-3">Bank Details</th>
              <th className="px-4 py-3 text-right">Amount</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-3 text-herb-500">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3"><span className="font-semibold text-herb-800">{r.name}</span> <span className="text-xs text-marigold-600">{r.member_id}</span></td>
                <td className="px-4 py-3 text-xs text-herb-500">
                  {r.bank_name ? (
                    <>
                      <div>{r.bank_name}</div>
                      <div>{r.bank_account} · {r.bank_ifsc}</div>
                    </>
                  ) : "—"}
                </td>
                <td className="px-4 py-3 text-right font-bold text-herb-700">₹{Number(r.amount).toFixed(2)}</td>
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
