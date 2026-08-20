import { useEffect, useState } from "react";
import api from "../../api";
import ProductCard from "../../components/ProductCard";

export default function OfferProducts() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    api.get("/catalog/products", { params: { offer: true } }).then((r) => setProducts(r.data)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-herb-800">Offer Products</h1>
        <p className="text-herb-500">Exclusive member-only offers and reward products.</p>
      </div>
      {products.length === 0 ? (
        <div className="card p-10 text-center text-herb-500">No offer products right now. Check back soon!</div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}
