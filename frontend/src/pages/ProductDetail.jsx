import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api from "../api";
import { useCart } from "../context/CartContext";

export default function ProductDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { add } = useCart();
  const [p, setP] = useState(null);
  const [qty, setQty] = useState(1);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    api.get(`/catalog/products/${slug}`).then((r) => setP(r.data)).catch(() => setNotFound(true));
  }, [slug]);

  if (notFound) return <div className="py-24 text-center text-herb-500">Product not found. <Link to="/products" className="text-marigold-600">Back to products</Link></div>;
  if (!p) return <div className="py-24 text-center text-herb-400">Loading…</div>;

  const off = p.mrp > p.price ? Math.round(((p.mrp - p.price) / p.mrp) * 100) : 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <Link to="/products" className="text-sm text-herb-500 hover:text-herb-700">← Back to products</Link>
      <div className="mt-4 grid gap-8 md:grid-cols-2">
        <div className="card overflow-hidden">
          <img src={p.image || "/static/products/logo.jpeg"} alt={p.name} className="w-full object-contain" />
        </div>
        <div>
          {p.is_offer && <span className="chip bg-marigold-500 text-white">Special Offer</span>}
          <h1 className="mt-2 text-3xl font-extrabold text-herb-800">{p.name}</h1>
          <div className="mt-3 flex items-center gap-3">
            <span className="text-3xl font-bold text-herb-700">₹{p.price}</span>
            {off > 0 && <span className="text-lg text-herb-400 line-through">₹{p.mrp}</span>}
            {off > 0 && <span className="chip bg-herb-100 text-herb-700">{off}% off</span>}
          </div>
          <div className="mt-1 font-semibold text-marigold-600">{p.sp} Selling Points (SP)</div>
          <p className="mt-4 text-herb-600">{p.description}</p>

          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            {["Ayurvedic Formulation", "No Side Effects", "Safe & Effective", "Trusted Quality"].map((t) => (
              <span key={t} className="chip bg-herb-50 text-herb-700 ring-1 ring-herb-100">✔ {t}</span>
            ))}
          </div>

          <div className="mt-6 flex items-center gap-3">
            <div className="flex items-center rounded-full ring-1 ring-herb-200">
              <button className="px-4 py-2 text-lg" onClick={() => setQty(Math.max(1, qty - 1))}>−</button>
              <span className="w-10 text-center font-semibold">{qty}</span>
              <button className="px-4 py-2 text-lg" onClick={() => setQty(qty + 1)}>+</button>
            </div>
            <button onClick={() => add(p, qty)} className="btn-primary flex-1 py-3">Add to Cart</button>
            <button onClick={() => { add(p, qty); navigate("/cart"); }} className="btn-accent flex-1 py-3">Buy Now</button>
          </div>
          <p className="mt-3 text-xs text-herb-400">
            Stock: {p.stock > 0 ? `${p.stock} available` : "Out of stock"}
          </p>
        </div>
      </div>
    </div>
  );
}
