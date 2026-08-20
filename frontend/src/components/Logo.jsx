import { Link } from "react-router-dom";

export default function Logo({ light = false, compact = false }) {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <img
        src="/static/products/logo.jpeg"
        alt="Arogyam Aradhya"
        className="h-11 w-11 rounded-full object-cover ring-2 ring-white/70 shadow"
      />
      {!compact && (
        <div className="leading-tight">
          <div className={`font-display text-lg font-extrabold ${light ? "text-white" : "text-herb-800"}`}>
            Arogyam <span className="text-marigold-500">Aradhya</span>
          </div>
          <div className={`text-[10px] font-medium ${light ? "text-herb-100" : "text-herb-500"}`}>
            स्वास्थ्य के प्रति श्रद्धा और विश्वास
          </div>
        </div>
      )}
    </Link>
  );
}
