import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import AuthModal from "../components/AuthModal";
import api from "../api";

export default function Cart() {
  const { items, setQty, remove, clear, totals } = useCart();
  const { auth } = useAuth();
  const navigate = useNavigate();
  const [modal, setModal] = useState(false);
  const [placing, setPlacing] = useState(false);
  const [done, setDone] = useState(null);
  const [error, setError] = useState("");

  const checkout = async () => {
    if (!auth || auth.role !== "member") {
      setModal(true);
      return;
    }
    setPlacing(true);
    setError("");
    try {
      const { data } = await api.post("/orders", {
        items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
      });
      clear();
      setDone(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not place order.");
    } finally {
      setPlacing(false);
    }
  };

  if (done) {
    const ordersLink = auth?.segment === "direct" ? "/seller/orders" : "/dashboard/orders";
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <div className="text-6xl">🧾</div>
        <h1 className="mt-4 text-2xl font-bold text-herb-800">Order Placed — Payment Pending</h1>
        <p className="mt-2 text-herb-500">Order <b>{done.order_no}</b> · ₹{done.total} · {done.total_sp} SP</p>
        <div className="mx-auto mt-5 max-w-md rounded-2xl bg-marigold-50 p-5 text-left text-sm text-marigold-800 ring-1 ring-marigold-100">
          <div className="font-semibold">Next step: complete your payment</div>
          <p className="mt-1">Pay <b>₹{done.total}</b> via UPI / bank transfer (see the Pay page), then share the reference with your sponsor/admin. Your order and points activate once the admin confirms payment.</p>
        </div>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link to="/pay" className="btn-accent">Payment Details</Link>
          <button onClick={() => navigate(ordersLink)} className="btn-primary">View Orders</button>
          <Link to="/products" className="btn-outline">Continue Shopping</Link>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <div className="text-6xl">🛒</div>
        <h1 className="mt-4 text-2xl font-bold text-herb-800">Your cart is empty</h1>
        <Link to="/products" className="btn-primary mt-6 inline-flex">Shop Products</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-extrabold text-herb-800">Your Cart</h1>
      {error && <div className="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700">{error}</div>}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {items.map((i) => (
            <div key={i.product_id} className="card flex items-center gap-4 p-3">
              <img src={i.image || "/static/products/logo.jpeg"} className="h-20 w-20 rounded-xl object-cover" alt="" />
              <div className="min-w-0 flex-1">
                <div className="truncate font-semibold text-herb-800">{i.name}</div>
                <div className="text-sm text-herb-500">₹{i.price} · {i.sp} SP</div>
              </div>
              <div className="flex items-center rounded-full ring-1 ring-herb-200">
                <button className="px-3 py-1.5" onClick={() => setQty(i.product_id, i.quantity - 1)}>−</button>
                <span className="w-8 text-center text-sm font-semibold">{i.quantity}</span>
                <button className="px-3 py-1.5" onClick={() => setQty(i.product_id, i.quantity + 1)}>+</button>
              </div>
              <div className="w-20 text-right font-bold text-herb-700">₹{i.price * i.quantity}</div>
              <button onClick={() => remove(i.product_id)} className="text-herb-300 hover:text-red-500">✕</button>
            </div>
          ))}
        </div>

        <div className="card h-fit p-6">
          <h3 className="mb-4 text-lg font-bold text-herb-800">Order Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-herb-500">Items</span><span>{totals.count}</span></div>
            <div className="flex justify-between"><span className="text-herb-500">Total SP</span><span className="font-semibold text-marigold-600">{totals.sp} SP</span></div>
            <div className="flex justify-between border-t border-herb-100 pt-3 text-base font-bold">
              <span>Total</span><span className="text-herb-700">₹{totals.amount}</span>
            </div>
          </div>
          <button onClick={checkout} disabled={placing} className="btn-primary mt-5 w-full py-3">
            {placing ? "Placing order…" : auth?.role === "member" ? "Place Order" : "Login & Checkout"}
          </button>
          <p className="mt-3 text-center text-xs text-herb-400">SP will be credited to your network on purchase.</p>
        </div>
      </div>
      <AuthModal open={modal} mode="login" onClose={() => setModal(false)} />
    </div>
  );
}
