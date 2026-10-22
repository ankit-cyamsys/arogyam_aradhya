import PageHeader from "../components/PageHeader";

const DOCS = [
  ["📄", "Business Plan (PDF)", "Complete binary compensation plan and income details.", null],
  ["📜", "Terms & Conditions", "Distributor agreement and code of conduct.", null],
  ["🧾", "Product Catalogue", "Full price list with SP values.", null],
  ["🏢", "GST Registration Certificate", "Company GST registration certificate.", "/static/site/gst-certificate.pdf"],
  ["🏭", "Udyam Registration Certificate", "MSME / Udyam registration certificate.", "/static/site/udyam-certificate.pdf"],
  ["🔒", "Privacy Policy", "How we handle your personal data.", null],
  ["↩️", "Refund & Return Policy", "Return, refund and cancellation terms.", null],
];

export default function Documents() {
  return (
    <div>
      <PageHeader icon="📁" title="Documents" subtitle="Download official company and business documents." />
      <div className="mx-auto max-w-5xl px-4 py-16">
        <div className="grid gap-4 sm:grid-cols-2">
          {DOCS.map(([icon, title, text, url]) => (
            <div key={title} className="card flex items-center gap-4 p-5">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-herb-100 text-2xl">{icon}</div>
              <div className="flex-1">
                <h3 className="font-bold text-herb-800">{title}</h3>
                <p className="text-sm text-herb-500">{text}</p>
              </div>
              {url ? (
                <a href={url} target="_blank" rel="noreferrer" className="btn-outline py-2">Download</a>
              ) : (
                <button className="btn-outline py-2" disabled>Download</button>
              )}
            </div>
          ))}
        </div>
        <p className="mt-6 text-center text-sm text-herb-400">More documents will be available for download once uploaded by the admin.</p>
      </div>
    </div>
  );
}
