import { useEffect, useState } from "react";
import api from "../api";

// Fetches an image from an authenticated API path (sends the Bearer token)
// and renders it via a blob object URL. `bust` changes force a refetch.
export default function AuthImage({ path, alt = "", className = "", bust = 0, fallback = null }) {
  const [url, setUrl] = useState(null);
  const [err, setErr] = useState(false);
  const [isPdf, setIsPdf] = useState(false);

  useEffect(() => {
    let objUrl;
    let cancelled = false;
    setErr(false); setUrl(null);
    api.get(path, { responseType: "blob" })
      .then((r) => {
        if (cancelled) return;
        setIsPdf((r.data.type || "").includes("pdf"));
        objUrl = URL.createObjectURL(r.data);
        setUrl(objUrl);
      })
      .catch(() => !cancelled && setErr(true));
    return () => { cancelled = true; if (objUrl) URL.revokeObjectURL(objUrl); };
  }, [path, bust]);

  if (err) return fallback;
  if (!url) return <div className={`animate-pulse bg-herb-50 ${className}`} />;
  if (isPdf) return <a href={url} target="_blank" rel="noreferrer" className={`grid place-items-center bg-herb-50 text-xs text-herb-600 ${className}`}>📄 View PDF</a>;
  return <img src={url} alt={alt} className={className} />;
}
