import { useEffect, useState } from "react";
import api from "../../api";
import StatCard from "../../components/StatCard";

function Node({ node, position, onExpand }) {
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
  const expandable = node.has_more;
  return (
    <div className="flex flex-col items-center">
      <button
        type="button"
        onClick={expandable ? () => onExpand(node.member_id) : undefined}
        title={node.is_active ? "Active" : "Inactive"}
        className={`relative grid h-16 w-16 place-items-center rounded-full text-2xl shadow ring-2 ${
          node.is_active ? "bg-herb-100 ring-herb-500" : "bg-slate-100 ring-slate-300"
        } ${expandable ? "cursor-pointer hover:ring-marigold-400" : "cursor-default"}`}
      >
        👤
        {expandable && (
          <span className="absolute -bottom-1 -right-1 grid h-5 w-5 place-items-center rounded-full bg-marigold-500 text-xs font-bold text-white ring-2 ring-white">
            +
          </span>
        )}
      </button>
      <div className="mt-1 max-w-[90px] truncate text-xs font-semibold text-herb-800">{node.name}</div>
      <div className="text-[10px] text-herb-500">{node.member_id}</div>
    </div>
  );
}

function Branch({ node, position, onExpand }) {
  const showChildren = node && (node.left || node.right);
  return (
    <div className="flex flex-col items-center">
      <Node node={node} position={position} onExpand={onExpand} />
      {showChildren && (
        <>
          <div className="h-6 w-px bg-herb-200" />
          <div className="flex items-start gap-6 sm:gap-10">
            <div className="flex flex-col items-center">
              <div className="mb-6 h-px w-16 bg-herb-200 sm:w-24" />
              <Branch node={node.left} position="L" onExpand={onExpand} />
            </div>
            <div className="flex flex-col items-center">
              <div className="mb-6 h-px w-16 bg-herb-200 sm:w-24" />
              <Branch node={node.right} position="R" onExpand={onExpand} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Replace the node matching `targetId` anywhere in the tree with the freshly
// fetched subtree rooted at it (immutable update so React re-renders).
function mergeNode(root, targetId, subtree) {
  if (!root) return root;
  if (root.member_id === targetId) {
    return { ...root, left: subtree.left, right: subtree.right, has_more: false };
  }
  return {
    ...root,
    left: mergeNode(root.left, targetId, subtree),
    right: mergeNode(root.right, targetId, subtree),
  };
}

export default function Team() {
  const [data, setData] = useState(null);
  const [treeData, setTreeData] = useState(null);

  useEffect(() => {
    api.get("/member/team").then((r) => {
      setData(r.data);
      setTreeData(r.data.tree);
    }).catch(() => {});
  }, []);

  const expand = async (memberId) => {
    try {
      const { data: subtree } = await api.get(`/member/tree/${memberId}`, { params: { depth: 3 } });
      setTreeData((prev) => mergeNode(prev, memberId, subtree));
    } catch (e) {
      alert(e.friendlyMessage || e.response?.data?.detail || "Could not load more of this branch.");
    }
  };

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
        <div className="mb-6 flex flex-wrap items-center gap-4 text-xs">
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full bg-herb-100 ring-2 ring-herb-500" /> Active</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full bg-slate-100 ring-2 ring-slate-300" /> Inactive</span>
          <span className="flex items-center gap-1"><span className="h-3 w-3 rounded-full border-2 border-dashed border-herb-200" /> Open slot</span>
          <span className="flex items-center gap-1"><span className="grid h-3 w-3 place-items-center rounded-full bg-marigold-500 text-[8px] font-bold text-white">+</span> Tap to load more</span>
        </div>
        <div className="flex min-w-max justify-center">
          <Branch node={treeData} onExpand={expand} />
        </div>
      </div>
    </div>
  );
}
