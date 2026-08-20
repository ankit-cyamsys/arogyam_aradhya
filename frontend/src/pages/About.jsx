import PageHeader from "../components/PageHeader";

export default function About() {
  return (
    <div>
      <PageHeader icon="🌿" title="About Arogyam Aradhya" subtitle="स्वास्थ्य के प्रति श्रद्धा और विश्वास — devotion and trust towards health." />
      <div className="mx-auto max-w-4xl px-4 py-16">
        <div className="prose max-w-none text-herb-700">
          <p className="text-lg leading-relaxed">
            Arogyam Aradhya is dedicated to bringing authentic Ayurvedic medicines and natural wellness
            products to every home. Rooted in ancient Indian wisdom and crafted with certified,
            high-quality herbs, our formulations are 100% natural, safe and effective.
          </p>
          <p className="mt-4 leading-relaxed">
            Beyond products, we empower people to build a livelihood through our transparent binary
            rewards network — where sharing good health with others becomes a rewarding business.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {[["🎯", "Our Mission", "Make authentic Ayurveda accessible and affordable for all."],
            ["👁️", "Our Vision", "A healthier society, one natural remedy at a time."],
            ["💚", "Our Values", "Purity, honesty, quality and community wellbeing."]].map(([i, t, d]) => (
            <div key={t} className="card p-6 text-center">
              <div className="mb-2 text-3xl">{i}</div>
              <h3 className="font-bold text-herb-800">{t}</h3>
              <p className="mt-1 text-sm text-herb-500">{d}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[["100%", "Natural"], ["50+", "Products"], ["1000s", "Members"], ["24×7", "Support"]].map(([n, l]) => (
            <div key={l} className="card p-6 text-center">
              <div className="text-2xl font-extrabold text-herb-700">{n}</div>
              <div className="text-sm text-herb-500">{l}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
