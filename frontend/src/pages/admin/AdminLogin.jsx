import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Logo from "../../components/Logo";

export default function AdminLogin() {
  const { adminLogin } = useAuth();
  const navigate = useNavigate();
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      await adminLogin(username, password);
      navigate("/admin");
    } catch (err) {
      setError(err.friendlyMessage || err.response?.data?.detail || "Login failed");
    } finally { setBusy(false); }
  };

  return (
    <div className="hero-gradient flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-2xl">
        <div className="mb-6 flex justify-center"><Logo /></div>
        <h1 className="mb-1 text-center text-xl font-bold text-herb-800">Admin Panel</h1>
        <p className="mb-6 text-center text-sm text-herb-500">Sign in to manage Arogyam Aradhya</p>
        {error && <div className="mb-4 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}
        <form onSubmit={submit} className="space-y-3">
          <div><label className="label">Username</label><input className="input" value={username} onChange={(e) => setU(e.target.value)} required /></div>
          <div><label className="label">Password</label><input className="input" type="password" value={password} onChange={(e) => setP(e.target.value)} required /></div>
          <button className="btn-primary w-full" disabled={busy}>{busy ? "Signing in…" : "Login"}</button>
        </form>
        <p className="mt-4 text-center text-xs text-herb-400">Default: admin / admin123</p>
      </div>
    </div>
  );
}
