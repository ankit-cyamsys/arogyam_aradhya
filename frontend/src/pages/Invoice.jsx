import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";

const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Invoice() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [inv, setInv] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get(`/orders/${orderId}/invoice`).then((r) => setInv(r.data)).catch(() => setErr("Invoice not found"));
  }, [orderId]);

  if (err) return <div className="p-10 text-center text-red-600">{err}</div>;
  if (!inv) return <div className="p-10 text-center text-herb-400">Loading invoice…</div>;

  const t = inv.totals;

  return (
    <div className="min-h-screen bg-herb-50/40 py-8">
      <div className="mx-auto max-w-3xl px-4">
        <div className="no-print mb-4 flex items-center justify-between">
          <button onClick={() => navigate(-1)} className="btn-outline py-2">← Back</button>
          <button onClick={() => window.print()} className="btn-primary py-2">🖨️ Print / Save PDF</button>
        </div>

        <div className="card overflow-hidden p-8" id="invoice">
          {/* Header */}
          <div className="flex items-start justify-between border-b border-herb-100 pb-4">
            <div className="flex items-center gap-3">
              <img src="/static/products/logo.jpeg" className="h-14 w-14 rounded-full" alt="" />
              <div>
                <div className="text-xl font-extrabold text-herb-800">{inv.seller.name}</div>
                <div className="text-xs text-herb-500">{inv.seller.address}</div>
                {inv.seller.gstin
                  ? <div className="text-xs font-semibold text-herb-700">GSTIN: {inv.seller.gstin}</div>
                  : <div className="text-xs text-red-500">GSTIN not set (add in Admin → GST settings)</div>}
                {inv.seller.phone && <div className="text-xs text-herb-500">📞 {inv.seller.phone}</div>}
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-herb-800">TAX INVOICE</div>
              <div className="text-sm text-herb-600">{inv.invoice_no}</div>
              <div className="text-xs text-herb-500">Date: {inv.date}</div>
            </div>
          </div>

          {/* Bill to */}
          <div className="grid grid-cols-2 gap-4 py-4 text-sm">
            <div>
              <div className="text-xs font-semibold uppercase text-herb-500">Bill To</div>
              <div className="font-semibold text-herb-800">{inv.buyer.name}</div>
              <div className="text-herb-600">{inv.buyer.address || "—"}</div>
              <div className="text-herb-500">ID: {inv.buyer.member_id} · 📞 {inv.buyer.phone || "—"}</div>
            </div>
            <div className="text-right">
              <div className="text-xs font-semibold uppercase text-herb-500">Place of Supply</div>
              <div className="text-herb-700">{inv.seller.state} ({inv.seller.state_code})</div>
              <div className="text-xs text-herb-500">{inv.intra_state ? "Intra-state (CGST + SGST)" : "Inter-state (IGST)"}</div>
            </div>
          </div>

          {/* Items */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
                <tr>
                  <th className="px-2 py-2">#</th>
                  <th className="px-2 py-2">Item</th>
                  <th className="px-2 py-2">HSN</th>
                  <th className="px-2 py-2 text-right">Qty</th>
                  <th className="px-2 py-2 text-right">Rate</th>
                  <th className="px-2 py-2 text-right">Taxable</th>
                  <th className="px-2 py-2 text-right">GST%</th>
                  <th className="px-2 py-2 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-herb-50">
                {inv.items.map((it, i) => (
                  <tr key={i}>
                    <td className="px-2 py-2">{i + 1}</td>
                    <td className="px-2 py-2 font-medium text-herb-800">{it.name}</td>
                    <td className="px-2 py-2 text-herb-500">{it.hsn}</td>
                    <td className="px-2 py-2 text-right">{it.qty}</td>
                    <td className="px-2 py-2 text-right">{inr(it.rate)}</td>
                    <td className="px-2 py-2 text-right">{inr(it.taxable)}</td>
                    <td className="px-2 py-2 text-right">{it.gst_rate}%</td>
                    <td className="px-2 py-2 text-right font-semibold">{inr(it.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Totals */}
          <div className="mt-4 flex justify-end">
            <div className="w-64 space-y-1 text-sm">
              <div className="flex justify-between"><span className="text-herb-500">Taxable Value</span><span>{inr(t.taxable)}</span></div>
              {inv.intra_state ? (
                <>
                  <div className="flex justify-between"><span className="text-herb-500">CGST</span><span>{inr(t.cgst)}</span></div>
                  <div className="flex justify-between"><span className="text-herb-500">SGST</span><span>{inr(t.sgst)}</span></div>
                </>
              ) : (
                <div className="flex justify-between"><span className="text-herb-500">IGST</span><span>{inr(t.igst)}</span></div>
              )}
              <div className="flex justify-between border-t border-herb-100 pt-2 text-base font-bold text-herb-800">
                <span>Grand Total</span><span>{inr(t.grand_total)}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-xl bg-herb-50 px-4 py-2 text-sm text-herb-700">
            <b>Amount in words:</b> {t.in_words}
          </div>

          <div className="mt-6 flex items-end justify-between text-xs text-herb-500">
            <div>This is a computer-generated invoice.</div>
            <div className="text-center">
              <div className="mb-6">For {inv.seller.name}</div>
              <div className="border-t border-herb-300 pt-1">Authorised Signatory</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
