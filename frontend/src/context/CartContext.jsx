import { createContext, useContext, useEffect, useMemo, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    const raw = localStorage.getItem("aa_cart");
    return raw ? JSON.parse(raw) : [];
  });

  useEffect(() => {
    localStorage.setItem("aa_cart", JSON.stringify(items));
  }, [items]);

  const add = (product, qty = 1) => {
    setItems((prev) => {
      const found = prev.find((i) => i.product_id === product.id);
      if (found) {
        return prev.map((i) =>
          i.product_id === product.id ? { ...i, quantity: i.quantity + qty } : i
        );
      }
      return [
        ...prev,
        {
          product_id: product.id,
          name: product.name,
          price: product.price,
          sp: product.sp,
          image: product.image,
          quantity: qty,
        },
      ];
    });
  };

  const setQty = (id, qty) =>
    setItems((prev) =>
      prev
        .map((i) => (i.product_id === id ? { ...i, quantity: Math.max(0, qty) } : i))
        .filter((i) => i.quantity > 0)
    );

  const remove = (id) => setItems((prev) => prev.filter((i) => i.product_id !== id));
  const clear = () => setItems([]);

  const totals = useMemo(() => {
    const amount = items.reduce((s, i) => s + i.price * i.quantity, 0);
    const sp = items.reduce((s, i) => s + i.sp * i.quantity, 0);
    const count = items.reduce((s, i) => s + i.quantity, 0);
    return { amount, sp, count };
  }, [items]);

  return (
    <CartContext.Provider value={{ items, add, setQty, remove, clear, totals }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
