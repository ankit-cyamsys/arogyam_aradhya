import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV = [
  ["📊", "Overview", "/admin"],
  ["🛍️", "Products", "/admin/products"],
  ["👥", "Members", "/admin/members"],
  ["💳", "Payouts", "/admin/payouts"],
  ["⚙️", "MLM Settings", "/admin/settings"],
];

export default function AdminLayout() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-slate-100">
      <div className="flex">
        <aside className="sticky top-0 hidden h-screen w-60 flex-col bg-herb-900 p-4 text-herb-100 md:flex">
          <div className="mb-6 flex items-center gap-2 px-2">
            <img src="/static/products/logo.jpeg" className="h-9 w-9 rounded-full" alt="" />
            <div>
              <div className="font-display font-bold text-white">Admin</div>
              <div className="text-[10px] text-herb-300">Arogyam Aradhya</div>
            </div>
          </div>
          <nav className="flex-1 space-y-1">
            {NAV.map(([icon, label, to]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/admin"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                    isActive ? "bg-herb-600 text-white" : "text-herb-200 hover:bg-herb-800"
                  }`
                }
              >
                <span>{icon}</span> {label}
              </NavLink>
            ))}
          </nav>
          <button onClick={() => { logout(); navigate("/admin/login"); }} className="btn-accent mt-4">
            Logout
          </button>
        </aside>
        <main className="min-h-screen flex-1 p-4 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
