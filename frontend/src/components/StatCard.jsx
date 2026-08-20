export default function StatCard({ label, value, unit = "", accent = "herb", icon }) {
  const ring = accent === "marigold" ? "ring-marigold-100" : "ring-herb-100";
  const text = accent === "marigold" ? "text-marigold-600" : "text-herb-700";
  return (
    <div className={`card p-5 ring-1 ${ring}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-herb-500">{label}</span>
        {icon && <span className="text-lg">{icon}</span>}
      </div>
      <div className={`mt-2 text-2xl font-extrabold ${text}`}>
        {value}
        {unit && <span className="ml-1 text-sm font-semibold text-herb-400">{unit}</span>}
      </div>
    </div>
  );
}
