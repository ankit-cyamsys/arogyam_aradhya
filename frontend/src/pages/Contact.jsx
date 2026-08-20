import { useState } from "react";
import PageHeader from "../components/PageHeader";

export default function Contact() {
  const [sent, setSent] = useState(false);
  return (
    <div>
      <PageHeader icon="✉️" title="Contact Us" subtitle="We'd love to hear from you. Reach out any time." />
      <div className="mx-auto grid max-w-5xl gap-8 px-4 py-16 md:grid-cols-2">
        <div className="space-y-4">
          {[["📞", "Phone", "+91 00000 00000"],
            ["✉️", "Email", "support@arogyamaradhya.com"],
            ["📍", "Address", "Varanasi, Uttar Pradesh, India"],
            ["🕒", "Hours", "Mon–Sat: 9AM – 6PM"]].map(([i, t, d]) => (
            <div key={t} className="card flex items-center gap-4 p-5">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-herb-100 text-2xl">{i}</div>
              <div>
                <div className="text-xs font-semibold uppercase text-herb-500">{t}</div>
                <div className="font-semibold text-herb-800">{d}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="card p-6">
          {sent ? (
            <div className="py-16 text-center">
              <div className="text-5xl">✅</div>
              <p className="mt-3 font-semibold text-herb-800">Thanks! We'll get back to you soon.</p>
            </div>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); setSent(true); }} className="space-y-3">
              <div><label className="label">Name</label><input className="input" required /></div>
              <div><label className="label">Email</label><input className="input" type="email" required /></div>
              <div><label className="label">Phone</label><input className="input" /></div>
              <div><label className="label">Message</label><textarea className="input" rows={4} required /></div>
              <button className="btn-primary w-full">Send Message</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
