import { useEffect, useState } from "react";
import api from "../api";
import ProductCard from "../components/ProductCard";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [active, setActive] = useState("");
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/catalog/categories").then((r) => setCategories(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .get("/catalog/products", { params: { category: active || undefined, q: q || undefined } })
      .then((r) => setProducts(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [active, q]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-herb-800">Our Products</h1>
        <p className="text-herb-500">Authentic Ayurvedic medicines & wellness essentials</p>
      </div>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActive("")}
            className={`chip px-4 py-2 ${active === "" ? "bg-herb-600 text-white" : "bg-white text-herb-700 ring-1 ring-herb-200"}`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.slug}
              onClick={() => setActive(c.slug)}
              className={`chip px-4 py-2 ${active === c.slug ? "bg-herb-600 text-white" : "bg-white text-herb-700 ring-1 ring-herb-200"}`}
            >
              {c.name}
            </button>
          ))}
        </div>
        <input
          className="input sm:max-w-xs"
          placeholder="Search products…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="py-20 text-center text-herb-400">Loading products…</div>
      ) : products.length === 0 ? (
        <div className="py-20 text-center text-herb-400">No products found.</div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}
