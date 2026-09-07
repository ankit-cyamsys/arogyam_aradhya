import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../api";

export default function Orders() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState(null);
  useEffect(() => {
    api.get("/orders").then((r) => setOrders(r.data)).catch(() => setOrders([]));
  }, []);

  if (!orders) return <div className="card p-6 text-herb-400">Loading orders…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">My Orders</h1>
      {orders.length === 0 ? (
        <div className="card p-10 text-center text-herb-500">
          No orders yet. <Link to="/products" className="font-semibold text-marigold-600">Shop now →</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => (
            <div key={o.id} className="card p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="font-bold text-herb-800">{o.order_no}</div>
                  <div className="text-xs text-herb-500">{new Date(o.created_at).toLocaleString()}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`chip capitalize ${
                    o.status === "paid" ? "bg-herb-100 text-herb-700"
                    : o.status === "cancelled" ? "bg-red-50 text-red-600"
                    : "bg-marigold-50 text-marigold-700"
                  }`}>{o.status === "pending" ? "⏳ pending" : o.status}</span>
                  <span className="font-bold text-herb-700">₹{o.total}</span>
                  <span className="chip bg-marigold-50 text-marigold-700">{o.total_sp} SP</span>
                  <button onClick={() => navigate(`/invoice/${o.id}`)} className="btn-outline py-1.5 text-xs">🧾 Invoice</button>
                </div>
              </div>
              <div className="mt-3 divide-y divide-herb-50 border-t border-herb-50 pt-2 text-sm">
                {o.items.map((it, i) => (
                  <div key={i} className="flex justify-between py-1.5">
                    <span className="text-herb-600">{it.name} × {it.quantity}</span>
                    <span className="text-herb-500">₹{it.price * it.quantity} · {it.sp * it.quantity} SP</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
