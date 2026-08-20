import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import api from "../api";

export default function Gallery() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    api.get("/catalog/products").then((r) => setProducts(r.data)).catch(() => {});
  }, []);
  return (
    <div>
      <PageHeader icon="🖼️" title="Gallery" subtitle="Our products, events and community moments." />
      <div className="mx-auto max-w-7xl px-4 py-16">
        <div className="columns-2 gap-4 sm:columns-3 lg:columns-4 [&>*]:mb-4">
          {products.map((p) => (
            <div key={p.id} className="card overflow-hidden">
              <img src={p.image} alt={p.name} className="w-full object-cover" />
              <div className="p-2 text-center text-xs font-semibold text-herb-700">{p.name}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
