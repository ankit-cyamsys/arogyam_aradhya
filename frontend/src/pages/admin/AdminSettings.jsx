import { useEffect, useState } from "react";
import api from "../../api";

const GROUPS = {
  matching: "Binary Matching (MLM)",
  level: "Level Bonus",
  direct: "Direct Selling (DSA)",
  economics: "Plan Economics",
  eligibility: "Activation & Eligibility",
  payout: "Payout",
  site: "Site / Company",
};

const META = {
  sp_currency_value: "₹ value per SP (1 SP = ₹10)",
  matching_ratio: "Left:Right ratio",
  matching_percent: "Matching payout %",
  daily_capping: "Capping per period (₹)",
  min_matching_pairs: "Min matched SP to earn",
  flush_unmatched: "Flush unmatched each period",
  direct_referral_bonus: "Direct referral bonus (₹)",
  level_bonus_percent: "Level % list e.g. [10,5,3,2,1]",
  dsa_percent: "Direct-seller commission %",
  mgmt_percent: "Management share %",
  company_profit_percent: "Company profit share %",
  product_cost_percent: "Product cost (COGS) %",
  payout_min_percent: "Total payout floor % of T/O",
  payout_max_percent: "Total payout ceiling % of T/O",
  activation_sp: "Activation SP",
  repurchase_sp: "Monthly repurchase SP",
  payout_min: "Min payout (₹)",
  admin_charge_percent: "Admin charge %",
  tds_percent: "TDS %",
  payout_day: "Weekly closing day",
  company_name: "Company name",
  support_phone: "Support phone",
  support_email: "Support email",
  address: "Company address",
};

const GROUP_OF = {
  sp_currency_value: "matching", matching_ratio: "matching", matching_percent: "matching",
  daily_capping: "matching", min_matching_pairs: "matching", flush_unmatched: "matching",
  direct_referral_bonus: "matching",
  level_bonus_percent: "level",
  dsa_percent: "direct", mgmt_percent: "direct", company_profit_percent: "direct",
  product_cost_percent: "economics", payout_min_percent: "economics", payout_max_percent: "economics",
  activation_sp: "eligibility", repurchase_sp: "eligibility",
  payout_min: "payout", admin_charge_percent: "payout", tds_percent: "payout", payout_day: "payout",
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
