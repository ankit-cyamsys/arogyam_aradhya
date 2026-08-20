import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";

export default function ProductCard({ product }) {
  const { add } = useCart();
  const off =
    product.mrp > product.price
      ? Math.round(((product.mrp - product.price) / product.mrp) * 100)
      : 0;

  return (
    <div className="card group flex flex-col overflow-hidden transition hover:-translate-y-1 hover:shadow-lg">
      <Link to={`/products/${product.slug}`} className="relative block aspect-square overflow-hidden bg-herb-50">
        <img
          src={product.image || "/static/products/logo.jpeg"}
          alt={product.name}
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
        {product.is_offer && (
          <span className="chip absolute left-2 top-2 bg-marigold-500 text-white">Offer</span>
        )}
        {off > 0 && (
          <span className="chip absolute right-2 top-2 bg-herb-600 text-white">{off}% off</span>
        )}
      </Link>
      <div className="flex flex-1 flex-col p-4">
        <Link to={`/products/${product.slug}`}>
          <h3 className="line-clamp-2 font-semibold text-herb-800 hover:text-herb-600">{product.name}</h3>
        </Link>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-lg font-bold text-herb-700">₹{product.price}</span>
          {off > 0 && <span className="text-sm text-herb-400 line-through">₹{product.mrp}</span>}
        </div>
        <div className="mt-1 text-xs font-semibold text-marigold-600">{product.sp} SP</div>
        <button onClick={() => add(product)} className="btn-primary mt-3 w-full py-2">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
