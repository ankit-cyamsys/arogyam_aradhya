import { useEffect, useState } from "react";
import api from "../../api";

const GROUPS = {
  matching: "Binary Matching & Capping (MLM)",
  direct: "Direct Selling (DSA)",
  gst: "GST / Invoicing",
  eligibility: "Activation & Eligibility",
  payout: "Payout",
  site: "Site / Company",
};

const META = {
  matching_per_sp: "₹ per matched SP (₹10 → 50 SP = ₹500)",
  matching_block_sp: "Matching block size (SP)",
  matching_ratio: "Left:Right ratio",
  capping_25sp: "Weekly cap ₹ (first purchase ≥25 SP)",
  capping_50sp: "Weekly cap ₹ (first purchase ≥50 SP)",
  capping_100sp: "Weekly cap ₹ (first purchase ≥100 SP)",
  gst_rate: "GST rate %",
  price_gst_inclusive: "Prices are GST-inclusive?",
  company_legal_name: "Legal business name",
  gstin: "Company GSTIN",
  company_address: "Company address",
  company_state: "Company state",
  company_state_code: "GST state code",
  hsn_default: "Default HSN/SAC code",
  invoice_prefix: "Invoice number prefix",
  dsa_percent: "Direct-seller commission %",
  activation_sp: "Greening SP (cumulative self-purchase)",
  payout_min: "Min payout (₹)",
  tds_percent: "TDS %",
  payout_day: "Weekly closing day",
  company_name: "Company name",
  support_phone: "Support phone",
  support_email: "Support email",
  address: "Company address",
};

const GROUP_OF = {
  matching_per_sp: "matching", matching_block_sp: "matching", matching_ratio: "matching",
  capping_25sp: "matching", capping_50sp: "matching", capping_100sp: "matching",
  gst_rate: "gst", price_gst_inclusive: "gst", company_legal_name: "gst", gstin: "gst",
  company_address: "gst", company_state: "gst", company_state_code: "gst",
  hsn_default: "gst", invoice_prefix: "gst",
  dsa_percent: "direct",
  activation_sp: "eligibility",
  payout_min: "payout", tds_percent: "payout", payout_day: "payout",
  company_name: "site", support_phone: "site", support_email: "site", address: "site",
};

export default function AdminSettings() {
  const [settings, setSettings] = useState({});
  const [saved, setSaved] = useState("");

  const load = () => api.get("/admin/settings").then((r) => setSettings(r.data));
  useEffect(() => { load(); }, []);

  const save = async (key, value) => {
    let parsed = value;
    if (Array.isArray(settings[key])) {
      try { parsed = JSON.parse(value); } catch { alert("Enter a valid list, e.g. [10,5,3]"); return; }
    } else if (typeof settings[key] === "number") {
      parsed = Number(value);
    } else if (typeof settings[key] === "boolean") {
      parsed = value === true || value === "true";
    }
    await api.put("/admin/settings", { key, value: parsed });
    setSaved(key);
    setTimeout(() => setSaved(""), 1500);
  };

  const grouped = {};
  Object.keys(settings).forEach((k) => {
    const g = GROUP_OF[k] || "site";
    (grouped[g] ||= []).push(k);
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-herb-800">MLM Settings</h1>
        <p className="text-herb-500">Tune your compensation plan. Changes apply to future calculations.</p>
      </div>

      {Object.entries(GROUPS).map(([g, label]) => (
        <div key={g} className="card p-6">
          <h2 className="mb-4 font-bold text-herb-800">{label}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {(grouped[g] || []).map((k) => (
              <Field key={k} k={k} value={settings[k]} label={META[k] || k} saved={saved === k}
                onSave={(v) => save(k, v)} isBool={typeof settings[k] === "boolean"}
                isList={Array.isArray(settings[k])} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function Field({ k, value, label, saved, onSave, isBool, isList }) {
  const [v, setV] = useState(isList ? JSON.stringify(value) : value);
  useEffect(() => { setV(isList ? JSON.stringify(value) : value); }, [value]);

  if (isBool) {
    return (
      <label className="flex items-center justify-between rounded-xl bg-herb-50 px-4 py-3">
        <span className="text-sm font-semibold text-herb-700">{label}</span>
        <input type="checkbox" checked={!!v} onChange={(e) => { setV(e.target.checked); onSave(e.target.checked); }} />
      </label>
    );
  }
  return (
    <div>
      <label className="label">{label} {saved && <span className="text-herb-500">✓ saved</span>}</label>
      <div className="flex gap-2">
        <input className="input" value={v ?? ""} onChange={(e) => setV(e.target.value)} />
        <button onClick={() => onSave(v)} className="btn-primary px-4">Save</button>
      </div>
      <div className="mt-1 text-[10px] uppercase text-herb-400">{k}</div>
    </div>
  );
}
