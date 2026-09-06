import { useEffect, useRef, useState } from "react";
import api from "../api";
import AuthImage from "./AuthImage";

const SLOTS = [
  ["profile_photo", "Profile Photo"],
  ["aadhaar_front", "Aadhaar Front"],
  ["aadhaar_back", "Aadhaar Back"],
  ["pan_front", "PAN Front"],
  ["pan_back", "PAN Back"],
];

export default function KycUploads() {
  const [status, setStatus] = useState({});
  const [bust, setBust] = useState({});
  const [busy, setBusy] = useState("");
  const inputs = useRef({});

  const load = () => api.get("/member/kyc").then((r) => setStatus(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const upload = async (docType, file) => {
    if (!file) return;
    setBusy(docType);
    const fd = new FormData();
    fd.append("file", file);
    try {
      await api.post(`/member/kyc/${docType}`, fd, { headers: { "Content-Type": "multipart/form-data" } });
      await load();
      setBust((b) => ({ ...b, [docType]: (b[docType] || 0) + 1 }));
    } catch (e) {
      alert(e.friendlyMessage || e.response?.data?.detail || "Upload failed");
    } finally {
      setBusy("");
    }
  };

  return (
    <div className="card p-6">
      <h2 className="mb-1 font-bold text-herb-800">KYC Documents</h2>
      <p className="mb-4 text-sm text-herb-500">Upload your documents (JPG/PNG/PDF, max 5 MB). They're stored securely for our records.</p>
      <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {SLOTS.map(([type, label]) => {
          const up = status[type]?.uploaded;
          return (
            <div key={type} className="rounded-xl border border-herb-100 p-3 text-center">
              <div className="mb-2 text-xs font-semibold text-herb-700">{label}</div>
              <div className="mx-auto mb-2 h-24 w-full overflow-hidden rounded-lg bg-herb-50">
                {up ? (
                  <AuthImage
                    path={`/member/kyc/${type}/file`}
                    bust={bust[type] || 0}
                    className="h-24 w-full object-cover"
                    alt={label}
                    fallback={<div className="grid h-24 place-items-center text-xs text-herb-400">Preview N/A</div>}
                  />
                ) : (
                  <div className="grid h-24 place-items-center text-2xl text-herb-300">＋</div>
                )}
              </div>
              <input
                ref={(el) => (inputs.current[type] = el)}
                type="file"
                accept="image/*,application/pdf"
                className="hidden"
                onChange={(e) => upload(type, e.target.files?.[0])}
              />
              <button
                onClick={() => inputs.current[type]?.click()}
                disabled={busy === type}
                className={`w-full py-1.5 text-xs ${up ? "btn-outline" : "btn-primary"}`}
              >
                {busy === type ? "Uploading…" : up ? "Replace" : "Upload"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
