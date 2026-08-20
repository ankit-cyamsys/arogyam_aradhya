import { useEffect, useState } from "react";
import api from "../../api";
import StatCard from "../../components/StatCard";

function Node({ node, position }) {
  if (!node) {
    return (
      <div className="flex flex-col items-center">
        <div className="grid h-16 w-16 place-items-center rounded-full border-2 border-dashed border-herb-200 text-herb-300">
          +
        </div>
        <div className="mt-1 text-[10px] text-herb-400">
          {position === "L" ? "Open Left" : position === "R" ? "Open Right" : "Empty"}
        </div>
      </div>
    );
  }
  return (
    <div className="flex flex-col items-center">
      <div
        className={`grid h-16 w-16 place-items-center rounded-full text-2xl shadow ring-2 ${
          node.is_active ? "bg-herb-100 ring-herb-500" : "bg-slate-100 ring-slate-300"
        }`}
        title={node.is_active ? "Active" : "Inactive"}
      >
        👤
      </div>
      <div className="mt-1 max-w-[90px] truncate text-xs font-semibold text-herb-800">{node.name}</div>
      <div className="text-[10px] text-herb-500">{node.member_id}</div>
    </div>
  );
}

function Branch({ node, depth = 0 }) {
  const hasChildren = node && (node.left || node.right || depth < 2);
  return (
    <div className="flex flex-col items-center">
      <Node node={node} />
      {node && depth < 2 && (
        <>
          <div className="h-6 w-px bg-herb-200" />
          <div className="flex items-start gap-6 sm:gap-10">
            <div className="flex flex-col items-center">
              <div className="mb-6 h-px w-16 bg-herb-200 sm:w-24" />
              <Branch node={node.left} depth={depth + 1} />
            </div>
            <div className="flex flex-col items-center">
              <div className="mb-6 h-px w-16 bg-herb-200 sm:w-24" />
              <Branch node={node.right} depth={depth + 1} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default function Team() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/member/team").then((r) => setData(r.data)).catch(() => {});
  }, []);

  if (!data) return <div className="card p-6 text-herb-400">Loading team…</div>;
  const c = data.counts;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-herb-800">My Team Tree</h1>
        <p className="text-herb-500">Binary structure of your organization</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Left Members" value={c.left} icon="⬅️" />
        <StatCard label="Right Members" value={c.right} icon="➡️" />
        <StatCard label="Left Active" value={c.left_active} accent="marigold" icon="✅" />
        <StatCard label="Right Active" value={c.right_active} accent="marigold" icon="✅" />
      </div>

      {data.parent && (
        <div className="card inline-flex items-center gap-3 p-4">
          <div className="grid h-10 w-10 place-items-center rounded-full bg-herb-100">👆</div>
          <div>
            <div className="text-xs text-herb-500">My Parent</div>
            <div className="font-semibold text-herb-800">{data.parent.name} · {data.parent.member_id}</div>
          </div>
        </div>
      )}

      <div className="card overflow-x-auto p-8">
        <div className="mb-6 flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full bg-herb-100 ring-2 ring-herb-500" /> Active</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full bg-slate-100 ring-2 ring-slate-300" /> Inactive</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full border-2 border-dashed border-herb-200" /> Open slot</span>
        </div>
        <div className="flex min-w-max justify-center">
          <Branch node={data.tree} />
        </div>
      </div>
    </div>
  );
}
