import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import Logo from "./Logo";
import AuthModal from "./AuthModal";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const LINKS = [
  ["Home", "/"],
  ["Products", "/products"],
  ["Franchise", "/franchise"],
  ["Documents", "/documents"],
  ["Pay", "/pay"],
  ["Gallery", "/gallery"],
  ["About", "/about"],
  ["Contact", "/contact"],
];

export default function Navbar() {
  const { auth, logout } = useAuth();
  const { totals } = useCart();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [modal, setModal] = useState(null); // 'login' | 'signup' | null

  return (
    <>
    <header className="glass sticky top-0 z-40 border-b border-herb-100/70">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Logo />

        <nav className="hidden items-center gap-1 lg:flex">
          {LINKS.map(([label, to]) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `rounded-full px-3.5 py-2 text-sm font-semibold transition ${
                  isActive ? "bg-herb-50 text-herb-700" : "text-herb-600 hover:text-herb-800"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link to="/cart" className="relative rounded-full p-2 text-herb-700 hover:bg-herb-50">
            <span className="text-xl">🛒</span>
            {totals.count > 0 && (
              <span className="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-marigold-500 text-[10px] font-bold text-white">
                {totals.count}
              </span>
            )}
          </Link>

          {auth?.role === "member" ? (
            <div className="hidden items-center gap-2 sm:flex">
              <button onClick={() => navigate("/dashboard")} className="btn-outline py-2">
                Dashboard
              </button>
              <button onClick={logout} className="btn-primary py-2">
                Logout
              </button>
            </div>
          ) : (
            <div className="hidden items-center gap-2 sm:flex">
              <button onClick={() => setModal("login")} className="btn-outline py-2">
                Login
              </button>
              <button onClick={() => navigate("/join")} className="btn-accent py-2">
                Join
              </button>
            </div>
          )}

          <button
            className="rounded-lg p-2 text-2xl text-herb-700 lg:hidden"
            onClick={() => setOpen(!open)}
          >
            ☰
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-herb-100 bg-white px-4 py-3 lg:hidden">
          <div className="flex flex-col gap-1">
            {LINKS.map(([label, to]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-semibold ${
                    isActive ? "bg-herb-50 text-herb-700" : "text-herb-600"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
            <div className="mt-2 flex gap-2">
              {auth?.role === "member" ? (
                <>
                  <button onClick={() => { setOpen(false); navigate("/dashboard"); }} className="btn-outline flex-1">
                    Dashboard
                  </button>
                  <button onClick={() => { setOpen(false); logout(); }} className="btn-primary flex-1">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <button onClick={() => { setOpen(false); setModal("login"); }} className="btn-outline flex-1">
                    Login
                  </button>
                  <button onClick={() => { setOpen(false); navigate("/join"); }} className="btn-accent flex-1">
                    Join
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

    </header>
    <AuthModal open={!!modal} mode={modal || "login"} onClose={() => setModal(null)} />
    </>
  );
}
