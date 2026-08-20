import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Logo from "../../components/Logo";

export default function SellerAuth({ mode = "login" }) {
  const { login, directSignup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "", password: "", name: "", phone: "", email: "", referral_code: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      if (mode === "login") {
        await login(form.username, form.password, "direct");
      } else {
        await directSignup({
          name: form.name, phone: form.phone, email: form.email || null,
          password: form.password, referral_code: form.referral_code || null,
        });
      }
      navigate("/seller");
    } catch (err) {
      setError(err.friendlyMessage || err.response?.data?.detail || "Something went wrong.");
    } finally { setBusy(false); }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-marigold-500 to-marigold-700 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
        <div className="mb-5 flex justify-center"><Logo /></div>
        <div className="mb-1 text-center">
          <span className="chip bg-marigold-100 text-marigold-700">🛍️ Direct Selling Portal</span>
        </div>
        <h1 className="mb-1 mt-2 text-center text-xl font-bold text-herb-800">
          {mode === "login" ? "Seller Login" : "Become a Direct Seller"}
        </h1>
        <p className="mb-5 text-center text-sm text-herb-500">Earn a flat 40% on every sale</p>

        {error && <div className="mb-4 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <form onSubmit={submit} className="space-y-3">
          {mode === "signup" && (
            <>
              <div><label className="label">Full Name</label><input className="input" value={form.name} onChange={upd("name")} required /></div>
              <div><label className="label">Phone</label><input className="input" value={form.phone} onChange={upd("phone")} required /></div>
              <div><label className="label">Email (optional)</label><input className="input" type="email" value={form.email} onChange={upd("email")} /></div>
              <div><label className="label">Referral Code (optional)</label><input className="input" value={form.referral_code} onChange={upd("referral_code")} /></div>
            </>
          )}
          {mode === "login" && (
            <div><label className="label">Member ID / Phone</label><input className="input" value={form.username} onChange={upd("username")} required /></div>
          )}
          <div><label className="label">Password</label><input className="input" type="password" value={form.password} onChange={upd("password")} required /></div>
          <button className="btn-accent w-full" disabled={busy}>
            {busy ? "Please wait…" : mode === "login" ? "Login" : "Create Seller Account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-herb-600">
          {mode === "login" ? "New seller? " : "Already a seller? "}
          <Link to={mode === "login" ? "/seller/signup" : "/seller/login"} className="font-semibold text-marigold-600 hover:underline">
            {mode === "login" ? "Sign up" : "Login"}
          </Link>
        </p>
        <p className="mt-2 text-center text-xs text-herb-400">
          Looking for the MLM network? <Link to="/join" className="text-herb-600 hover:underline">Switch portal</Link>
        </p>
      </div>
    </div>
  );
}
