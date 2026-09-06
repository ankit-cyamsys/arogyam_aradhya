import { useEffect, useState } from "react";
import api from "../../api";
import KycUploads from "../../components/KycUploads";
import ChangePassword from "../../components/ChangePassword";

const FIELDS = [
  ["email", "Email", "email"],
  ["address", "Address", "text"],
  ["city", "City", "text"],
  ["state", "State", "text"],
  ["pincode", "Pincode", "text"],
  ["pan", "PAN", "text"],
  ["aadhaar", "Aadhaar", "text"],
  ["nominee", "Nominee", "text"],
  ["bank_name", "Bank Name", "text"],
  ["bank_account", "Account Number", "text"],
  ["bank_ifsc", "IFSC Code", "text"],
];

export default function Profile() {
  const [me, setMe] = useState(null);
  const [form, setForm] = useState({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.get("/member/me").then((r) => { setMe(r.data); setForm(r.data); }).catch(() => {});
  }, []);

  const save = async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(FIELDS.map(([k]) => [k, form[k] || null]));
    const { data } = await api.put("/member/me", payload);
    setMe(data);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  if (!me) return <div className="card p-6 text-herb-400">Loading…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">My Profile</h1>

      <div className="card p-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="grid h-16 w-16 place-items-center rounded-full bg-herb-100 text-3xl">👤</div>
          <div>
            <div className="text-lg font-bold text-herb-800">{me.name}</div>
            <div className="text-sm text-herb-500">{me.member_id} · {me.phone}</div>
          </div>
          <span className={`chip ml-auto ${me.is_active ? "bg-herb-100 text-herb-700" : "bg-slate-100 text-slate-500"}`}>
            {me.is_active ? "● Active" : "○ Inactive"}
          </span>
        </div>
      </div>

      <form onSubmit={save} className="card p-6">
        <h2 className="mb-4 font-bold text-herb-800">KYC & Bank Details</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {FIELDS.map(([k, label, type]) => (
            <div key={k}>
              <label className="label">{label}</label>
              <input
                className="input"
                type={type}
                value={form[k] || ""}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              />
            </div>
          ))}
        </div>
        <div className="mt-5 flex items-center gap-3">
          <button className="btn-primary">Save Changes</button>
          {saved && <span className="text-sm font-semibold text-herb-600">✓ Saved</span>}
        </div>
      </form>

      <KycUploads />
      <ChangePassword />
    </div>
  );
}
