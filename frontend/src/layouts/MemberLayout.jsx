import { useState } from "react";
import { NavLink, Outlet, useNavigate, Link } from "react-router-dom";
import Logo from "../components/Logo";
import { useAuth } from "../context/AuthContext";

const NAV = [
  ["📊", "Dashboard", "/dashboard"],
  ["👤", "Profile", "/dashboard/profile"],
  ["🌳", "My Team", "/dashboard/team"],
  ["🏆", "Level Bonus", "/dashboard/level-bonus"],
  ["📦", "My Orders", "/dashboard/orders"],
  ["💰", "Bonus", "/dashboard/bonus"],
  ["💳", "Payout", "/dashboard/payout"],
  ["🎁", "Offers", "/dashboard/offers"],
  ["🛍️", "Offer Products", "/dashboard/offer-products"],
  ["🪪", "ID Card", "/dashboard/id-card"],
];

export default function MemberLayout() {
  const { auth, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-herb-50/50 leaf-pattern">
      <header className="sticky top-0 z-40 border-b border-herb-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <button className="rounded-lg p-1.5 text-2xl text-herb-700 lg:hidden" onClick={() => setOpen(!open)}>☰</button>
            <Logo />
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm font-semibold text-herb-700 sm:block">
              👋 {auth?.name}
            </span>
            <Link to="/" className="btn-outline py-2">Store</Link>
            <button onClick={() => { logout(); navigate("/"); }} className="btn-primary py-2">Logout</button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        <aside className={`${open ? "block" : "hidden"} lg:block`}>
          <nav className="card sticky top-20 w-60 overflow-hidden p-2">
            {NAV.map(([icon, label, to]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/dashboard"}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                    isActive ? "bg-herb-600 text-white shadow" : "text-herb-700 hover:bg-herb-50"
                  }`
                }
              >
                <span className="text-base">{icon}</span>
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
