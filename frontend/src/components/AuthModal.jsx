import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AuthModal({ open, mode: initialMode = "login", onClose }) {
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState(initialMode);
  const [form, setForm] = useState({
    username: "",
    password: "",
    name: "",
    phone: "",
    email: "",
    sponsor_id: "",
    position: "L",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPw, setShowPw] = useState(false);

  if (!open) return null;

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "login") {
        await login(form.username, form.password, "mlm");
      } else {
        await signup({
          name: form.name,
          phone: form.phone,
          email: form.email || null,
          password: form.password,
          sponsor_id: form.sponsor_id,
          position: form.position,
        });
      }
      onClose?.();
      navigate("/dashboard");
    } catch (err) {
      setError(err.friendlyMessage || err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="card w-full max-w-md p-6 sm:p-8" onClick={(e) => e.stopPropagation()}>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-xl font-bold text-herb-800">
            {mode === "login" ? "Member Login" : "Join the Network"}
          </h2>
          <button onClick={onClose} className="text-2xl leading-none text-herb-400 hover:text-herb-700">
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700 ring-1 ring-red-100">
            {error}
          </div>
        )}

        <form onSubmit={submit} className="space-y-3.5">
          {mode === "signup" && (
            <>
              <div>
                <label className="label">Full Name</label>
                <input className="input" value={form.name} onChange={update("name")} required />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Phone</label>
                  <input className="input" value={form.phone} onChange={update("phone")} required />
                </div>
                <div>
                  <label className="label">Leg</label>
                  <select className="input" value={form.position} onChange={update("position")}>
                    <option value="L">Left</option>
                    <option value="R">Right</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Email (optional)</label>
                <input className="input" type="email" value={form.email} onChange={update("email")} />
              </div>
              <div>
                <label className="label">Sponsor ID</label>
                <input
                  className="input"
                  placeholder="e.g. AA47818100"
                  value={form.sponsor_id}
                  onChange={update("sponsor_id")}
                  required
                />
              </div>
            </>
          )}

          {mode === "login" && (
            <div>
              <label className="label">Member ID / Phone</label>
              <input className="input" value={form.username} onChange={update("username")} required />
            </div>
          )}

          <div>
            <label className="label">Password</label>
            <div className="relative">
              <input
                className="input pr-12"
                type={showPw ? "text" : "password"}
                value={form.password}
                onChange={update("password")}
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sm"
              >
                {showPw ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          <button type="submit" className="btn-primary w-full" disabled={busy}>
            {busy ? "Please wait…" : mode === "login" ? "Login" : "Create Account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-herb-600">
          {mode === "login" ? "New here? " : "Already a member? "}
          <button
            className="font-semibold text-marigold-600 hover:underline"
            onClick={() => {
              setError("");
              setMode(mode === "login" ? "signup" : "login");
            }}
          >
            {mode === "login" ? "Sign up" : "Login"}
          </button>
        </p>
      </div>
    </div>
  );
}
