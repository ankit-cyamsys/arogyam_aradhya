import PageHeader from "../components/PageHeader";

const DOCS = [
  ["📄", "Business Plan (PDF)", "Complete binary compensation plan and income details."],
  ["📜", "Terms & Conditions", "Distributor agreement and code of conduct."],
  ["🧾", "Product Catalogue", "Full price list with SP values."],
  ["🏢", "Company Registration", "LLP / GST and incorporation documents."],
  ["🔒", "Privacy Policy", "How we handle your personal data."],
  ["↩️", "Refund & Return Policy", "Return, refund and cancellation terms."],
];

export default function Documents() {
  return (
    <div>
      <PageHeader icon="📁" title="Documents" subtitle="Download official company and business documents." />
      <div className="mx-auto max-w-5xl px-4 py-16">
        <div className="grid gap-4 sm:grid-cols-2">
          {DOCS.map(([icon, title, text]) => (
            <div key={title} className="card flex items-center gap-4 p-5">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-herb-100 text-2xl">{icon}</div>
              <div className="flex-1">
                <h3 className="font-bold text-herb-800">{title}</h3>
                <p className="text-sm text-herb-500">{text}</p>
              </div>
              <button className="btn-outline py-2" disabled>Download</button>
            </div>
          ))}
        </div>
        <p className="mt-6 text-center text-sm text-herb-400">Documents will be available for download once uploaded by the admin.</p>
      </div>
    </div>
  );
}
