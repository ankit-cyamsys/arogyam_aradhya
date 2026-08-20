import { useEffect, useState } from "react";
import api from "../../api";

const BLANK = { name: "", category_id: "", mrp: 0, price: 0, cost_price: 0, sp: 0, stock: 0, image: "", description: "", is_active: true, is_offer: false };

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [cats, setCats] = useState([]);
  const [form, setForm] = useState(BLANK);
  const [editing, setEditing] = useState(null);

  const load = () => api.get("/catalog/products").then((r) => setProducts(r.data));
  useEffect(() => {
    load();
    api.get("/catalog/categories").then((r) => setCats(r.data));
  }, []);

  const save = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
      mrp: Number(form.mrp), price: Number(form.price), cost_price: Number(form.cost_price),
      sp: Number(form.sp), stock: Number(form.stock),
    };
    if (editing) await api.put(`/admin/products/${editing}`, payload);
    else await api.post("/admin/products", payload);
    setForm(BLANK); setEditing(null); load();
  };

  const edit = (p) => { setEditing(p.id); setForm({ ...p, category_id: p.category_id || "" }); };
  const del = async (id) => { if (confirm("Deactivate this product?")) { await api.delete(`/admin/products/${id}`); load(); } };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">Products</h1>

      <form onSubmit={save} className="card grid gap-3 p-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="sm:col-span-2 lg:col-span-3 font-bold text-herb-800">{editing ? "Edit Product" : "Add Product"}</div>
        <div><label className="label">Name</label><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
        <div><label className="label">Category</label>
          <select className="input" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">—</option>
            {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div><label className="label">Image URL</label><input className="input" value={form.image || ""} onChange={(e) => setForm({ ...form, image: e.target.value })} placeholder="/static/products/p01.jpeg" /></div>
        <div><label className="label">MRP</label><input className="input" type="number" value={form.mrp} onChange={(e) => setForm({ ...form, mrp: e.target.value })} /></div>
        <div><label className="label">Price (DP)</label><input className="input" type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /></div>
        <div><label className="label">Cost Price</label><input className="input" type="number" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} /></div>
        <div><label className="label">SP</label><input className="input" type="number" value={form.sp} onChange={(e) => setForm({ ...form, sp: e.target.value })} /></div>
        <div><label className="label">Stock</label><input className="input" type="number" value={form.stock} onChange={(e) => setForm({ ...form, stock: e.target.value })} /></div>
        <div className="flex items-end gap-4">
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active</label>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_offer} onChange={(e) => setForm({ ...form, is_offer: e.target.checked })} /> Offer</label>
        </div>
        <div className="sm:col-span-2 lg:col-span-3 flex gap-2">
          <button className="btn-primary">{editing ? "Update" : "Add Product"}</button>
          {editing && <button type="button" onClick={() => { setForm(BLANK); setEditing(null); }} className="btn-outline">Cancel</button>}
        </div>
      </form>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr><th className="px-4 py-3">Product</th><th className="px-4 py-3">Price</th><th className="px-4 py-3">SP</th><th className="px-4 py-3">Stock</th><th className="px-4 py-3">Status</th><th className="px-4 py-3"></th></tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {products.map((p) => (
              <tr key={p.id}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <img src={p.image} className="h-10 w-10 rounded-lg object-cover" alt="" />
                    <span className="font-semibold text-herb-800">{p.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3">₹{p.price}</td>
                <td className="px-4 py-3">{p.sp}</td>
                <td className="px-4 py-3">{p.stock}</td>
                <td className="px-4 py-3">
                  {p.is_offer && <span className="chip mr-1 bg-marigold-50 text-marigold-700">Offer</span>}
                  <span className={`chip ${p.is_active ? "bg-herb-100 text-herb-700" : "bg-slate-100 text-slate-500"}`}>{p.is_active ? "Active" : "Off"}</span>
                </td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => edit(p)} className="mr-2 text-herb-600 hover:underline">Edit</button>
                  <button onClick={() => del(p.id)} className="text-red-500 hover:underline">Del</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
