import { useEffect, useState } from "react";
import api from "../../api";

const sp = (n) => Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}
function monthStartStr() {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10);
}

export default function AdminSpReport() {
  const [preset, setPreset] = useState("month");
  const [from, setFrom] = useState(monthStartStr());
  const [to, setTo] = useState(todayStr());
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    api.get("/admin/reports/sp", { params: { date_from: from || undefined, date_to: to || undefined } })
      .then((r) => setRows(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const applyPreset = (p) => {
    setPreset(p);
    if (p === "today") { setFrom(todayStr()); setTo(todayStr()); }
    else if (p === "month") { setFrom(monthStartStr()); setTo(todayStr()); }
    // "custom" leaves from/to as whatever the user picks
  };

  const totals = rows.reduce((a, r) => ({ self: a.self + r.self_sp, team: a.team + r.team_sp, total: a.total + r.total_sp }), { self: 0, team: 0, total: 0 });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">SP Report</h1>

      <div className="card flex flex-wrap items-end gap-4 p-5">
        <div className="flex gap-2">
          {[["today", "Today"], ["month", "This Month"], ["custom", "Custom"]].map(([key, label]) => (
            <button key={key} onClick={() => applyPreset(key)}
              className={`chip px-3 py-1.5 ${preset === key ? "bg-herb-600 text-white" : "bg-white text-herb-600 ring-1 ring-herb-200"}`}>
              {label}
            </button>
          ))}
        </div>
        <div>
          <label className="label">From</label>
          <input type="date" className="input" value={from} onChange={(e) => { setFrom(e.target.value); setPreset("custom"); }} />
        </div>
        <div>
          <label className="label">To</label>
          <input type="date" className="input" value={to} onChange={(e) => { setTo(e.target.value); setPreset("custom"); }} />
        </div>
        <button onClick={load} disabled={loading} className="btn-primary">{loading ? "Loading…" : "Apply"}</button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="card p-5"><div className="text-xs text-herb-500">Total Self SP</div><div className="text-xl font-bold text-herb-800">{sp(totals.self)}</div></div>
        <div className="card p-5"><div className="text-xs text-herb-500">Total Team SP</div><div className="text-xl font-bold text-herb-800">{sp(totals.team)}</div></div>
        <div className="card p-5"><div className="text-xs text-herb-500">Grand Total SP</div><div className="text-xl font-bold text-marigold-600">{sp(totals.total)}</div></div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-herb-50 text-left text-xs uppercase text-herb-600">
            <tr>
              <th className="px-4 py-3">Member ID</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Portal</th>
              <th className="px-4 py-3 text-right">Self SP</th><th className="px-4 py-3 text-right">Team SP</th><th className="px-4 py-3 text-right">Total SP</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-herb-50">
            {rows.map((r) => (
              <tr key={r.member_id}>
                <td className="px-4 py-3 font-semibold text-marigold-600">{r.member_id}</td>
                <td className="px-4 py-3 text-herb-800">{r.name}</td>
                <td className="px-4 py-3">
                  <span className={`chip ${r.segment === "direct" ? "bg-marigold-50 text-marigold-700" : "bg-herb-50 text-herb-700"}`}>
                    {r.segment === "direct" ? "Direct" : "MLM"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">{sp(r.self_sp)}</td>
                <td className="px-4 py-3 text-right">{sp(r.team_sp)}</td>
                <td className="px-4 py-3 text-right font-bold text-herb-700">{sp(r.total_sp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <div className="p-8 text-center text-herb-400">No SP activity in this period.</div>}
      </div>
    </div>
  );
}
