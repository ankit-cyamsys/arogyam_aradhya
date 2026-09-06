import { useState } from "react";
import api from "../api";

export default function ChangePassword() {
  const [f, setF] = useState({ current_password: "", new_password: "", confirm: "" });
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);
  const upd = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setMsg(null);
    if (f.new_password.length < 6) return setMsg({ ok: false, text: "New password must be at least 6 characters" });
    if (f.new_password !== f.confirm) return setMsg({ ok: false, text: "New passwords do not match" });
    setBusy(true);
    try {
      await api.post("/member/change-password", { current_password: f.current_password, new_password: f.new_password });
      setMsg({ ok: true, text: "Password changed successfully" });
      setF({ current_password: "", new_password: "", confirm: "" });
    } catch (err) {
      setMsg({ ok: false, text: err.friendlyMessage || err.response?.data?.detail || "Could not change password" });
    } finally { setBusy(false); }
  };

  return (
    <form onSubmit={submit} className="card p-6">
      <h2 className="mb-4 font-bold text-herb-800">Change Password</h2>
      <div className="grid gap-4 sm:grid-cols-3">
        <div><label className="label">Current Password</label><input className="input" type="password" value={f.current_password} onChange={upd("current_password")} required /></div>
        <div><label className="label">New Password</label><input className="input" type="password" value={f.new_password} onChange={upd("new_password")} minLength={6} required /></div>
        <div><label className="label">Confirm New Password</label><input className="input" type="password" value={f.confirm} onChange={upd("confirm")} minLength={6} required /></div>
      </div>
      <div className="mt-4 flex items-center gap-3">
        <button className="btn-primary" disabled={busy}>{busy ? "Saving…" : "Update Password"}</button>
        {msg && <span className={`text-sm font-semibold ${msg.ok ? "text-herb-600" : "text-red-600"}`}>{msg.text}</span>}
      </div>
    </form>
  );
}
