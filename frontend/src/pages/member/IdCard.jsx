import { useEffect, useState } from "react";
import api from "../../api";

export default function IdCard() {
  const [c, setC] = useState(null);
  const [stats, setStats] = useState(null);
  useEffect(() => {
    api.get("/mlm/idcard").then((r) => setC(r.data)).catch(() => {});
    api.get("/member/dashboard").then((r) => setStats(r.data)).catch(() => {});
  }, []);

  if (!c) return <div className="card p-6 text-herb-400">Loading…</div>;
  const validTill = c.joined
    ? new Date(new Date(c.joined).setFullYear(new Date(c.joined).getFullYear() + 1)).toLocaleDateString()
    : "—";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-herb-800">Distributor ID Card</h1>

      <div className="mx-auto max-w-md">
        <div className="overflow-hidden rounded-2xl shadow-xl ring-1 ring-herb-100">
          <div className="hero-gradient flex items-center justify-between px-6 py-4 text-white">
            <div className="flex items-center gap-3">
              <img src="/static/products/logo.jpeg" className="h-12 w-12 rounded-full ring-2 ring-white/70" alt="" />
              <div>
                <div className="font-display text-lg font-extrabold leading-tight">
                  Arogyam <span className="text-marigold-300">Aradhya</span>
                </div>
                <div className="text-[10px] text-herb-100">DISTRIBUTOR IDENTITY CARD</div>
              </div>
            </div>
            {stats?.rank_tier && <span className="chip bg-marigold-400 text-white">{stats.rank_tier}</span>}
          </div>
          <div className="bg-white p-6">
            <div className="flex items-center gap-4">
              <div className="grid h-20 w-20 place-items-center rounded-xl bg-herb-50 text-4xl ring-1 ring-herb-100">👤</div>
              <div>
                <div className="text-lg font-bold text-herb-800">{c.name}</div>
                <div className="text-sm font-semibold text-marigold-600">{c.member_id}</div>
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <span className={`chip ${c.is_active ? "bg-herb-100 text-herb-700" : "bg-slate-100 text-slate-500"}`}>
                    {c.is_active ? "● Active" : "○ Inactive"}
                  </span>
                  {stats?.rank_name && <span className="chip bg-marigold-50 text-marigold-700">🏆 {stats.rank_name}</span>}
                </div>
              </div>
            </div>
            <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-xs text-herb-500">Mobile</dt><dd className="font-semibold text-herb-800">{c.phone || "—"}</dd></div>
              <div><dt className="text-xs text-herb-500">Joining</dt><dd className="font-semibold text-herb-800">{c.joined || "—"}</dd></div>
              <div><dt className="text-xs text-herb-500">Valid Till</dt><dd className="font-semibold text-herb-800">{validTill}</dd></div>
              <div><dt className="text-xs text-herb-500">Rank</dt><dd className="font-semibold text-herb-800">{stats?.rank_name || "—"}</dd></div>
            </dl>
          </div>
          <div className="bg-herb-900 px-6 py-2 text-center text-[10px] text-herb-200">
            This card certifies the holder as a registered distributor of {c.company}.
          </div>
        </div>
        <button onClick={() => window.print()} className="btn-outline mt-5 w-full">🖨️ Print / Save as PDF</button>
      </div>
    </div>
  );
}
