import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import ProductCard from "../components/ProductCard";

const SLIDES = [
  { icon: "🌿", title: "Ancient Wisdom, Modern Wellness", text: "Authentic Ayurvedic medicines for natural healing", cta: ["Explore Products", "/products"] },
  { icon: "🤝", title: "Join Our Wellness Community", text: "Share health, earn rewards, grow together", cta: ["Get Started", "/franchise"] },
  { icon: "💰", title: "Earn While You Heal", text: "Build your wellness business with our binary rewards plan", cta: ["Join Network", "/franchise"] },
  { icon: "🎁", title: "Exclusive Member Benefits", text: "Special discounts, bonuses and rewards for our community", cta: ["View Offers", "/products"] },
];

const STEPS = [
  ["🔍", "Browse", "Explore our collection of authentic Ayurvedic products"],
  ["🛒", "Add to Cart", "Select your products and add them to your cart"],
  ["📦", "Get Delivered", "Receive your order at your doorstep"],
];

const FEATURES = [
  ["✅", "100% Natural & Certified", "Authentic Ayurvedic formulations from certified manufacturers"],
  ["🚚", "Fast Delivery", "Quick and reliable delivery to your doorstep"],
  ["💰", "Best Prices", "Competitive pricing with transparent costs"],
  ["🔒", "Secure Payments", "Safe and secure payment processing"],
];

const REVIEWS = [
  ["Priya Sharma", "Excellent quality products! The Ayurvedic medicines are authentic and effective. Highly recommended!"],
  ["Rajesh Kumar", "Great service and fast delivery. The products have really helped improve my health naturally."],
  ["Anita Desai", "Trustworthy platform with genuine Ayurvedic products. The community support is amazing!"],
];

export default function Home() {
  const [products, setProducts] = useState([]);
  const [slide, setSlide] = useState(0);

  useEffect(() => {
    api.get("/catalog/products").then((r) => setProducts(r.data.slice(0, 10))).catch(() => {});
  }, []);

  useEffect(() => {
    const t = setInterval(() => setSlide((s) => (s + 1) % SLIDES.length), 4500);
    return () => clearInterval(t);
  }, []);

  const s = SLIDES[slide];

  return (
    <div>
      {/* Hero */}
      <section className="hero-gradient relative overflow-hidden text-white">
        <div className="leaf-pattern absolute inset-0 opacity-30" />
        <div className="relative mx-auto flex max-w-7xl flex-col items-center gap-6 px-4 py-20 text-center sm:py-28">
          <img
            src="/static/products/logo.jpeg"
            alt="Arogyam Aradhya"
            className="h-20 w-20 rounded-full object-cover shadow-xl ring-4 ring-white/25"
          />
          <span className="chip bg-white/15 px-4 py-1.5 text-herb-50 ring-1 ring-white/25">
            {s.icon} स्वास्थ्य के प्रति श्रद्धा और विश्वास
          </span>
          <h1 key={slide} className="animate-fade-up max-w-3xl text-3xl font-extrabold leading-tight drop-shadow-sm sm:text-5xl">
            {s.title}
          </h1>
          <p className="max-w-xl text-herb-100 sm:text-lg">{s.text}</p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link to={s.cta[1]} className="btn-accent px-7 py-3 text-base">{s.cta[0]}</Link>
            <Link to="/join" className="btn-outline border-white/40 bg-white/10 px-7 py-3 text-base text-white hover:bg-white/20 hover:text-white">
              Join the Network
            </Link>
          </div>
          <div className="mt-2 flex gap-2">
            {SLIDES.map((_, i) => (
              <button
                key={i}
                onClick={() => setSlide(i)}
                aria-label={`Slide ${i + 1}`}
                className={`h-2 rounded-full transition-all ${i === slide ? "w-8 bg-marigold-400" : "w-2 bg-white/40 hover:bg-white/60"}`}
              />
            ))}
          </div>
          <div className="mt-6 grid w-full max-w-2xl grid-cols-3 gap-3 border-t border-white/15 pt-6 text-center">
            {[["100%", "Natural & Certified"], ["50+", "Ayurvedic Products"], ["40%", "Direct Seller Margin"]].map(([n, l]) => (
              <div key={l}>
                <div className="text-2xl font-extrabold text-marigold-300">{n}</div>
                <div className="text-xs text-herb-100">{l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Products strip */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold text-herb-800 sm:text-3xl">Featured Products</h2>
            <p className="text-herb-500">Handpicked Ayurvedic essentials for your family</p>
          </div>
          <Link to="/products" className="btn-outline hidden sm:inline-flex">View All →</Link>
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-herb-50/70 py-16">
        <div className="mx-auto max-w-7xl px-4">
          <h2 className="mb-10 text-center text-2xl font-bold text-herb-800 sm:text-3xl">How It Works</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {STEPS.map(([icon, title, text], i) => (
              <div key={title} className="card p-8 text-center">
                <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-full bg-herb-100 text-3xl">{icon}</div>
                <div className="mb-1 text-sm font-bold text-marigold-600">STEP {i + 1}</div>
                <h3 className="mb-2 text-lg font-bold text-herb-800">{title}</h3>
                <p className="text-sm text-herb-500">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <h2 className="mb-10 text-center text-2xl font-bold text-herb-800 sm:text-3xl">Why Choose Arogyam Aradhya?</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(([icon, title, text]) => (
            <div key={title} className="card p-6 text-center">
              <div className="mb-3 text-4xl">{icon}</div>
              <h3 className="mb-2 font-bold text-herb-800">{title}</h3>
              <p className="text-sm text-herb-500">{text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-herb-900 py-16 text-white">
        <div className="mx-auto max-w-7xl px-4">
          <h2 className="mb-10 text-center text-2xl font-bold sm:text-3xl">What Our Customers Say</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {REVIEWS.map(([name, text]) => (
              <div key={name} className="rounded-2xl bg-herb-800 p-6">
                <div className="mb-3 text-marigold-400">★★★★★</div>
                <p className="mb-4 text-herb-100">"{text}"</p>
                <div className="font-semibold text-white">— {name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-5xl px-4 py-20 text-center">
        <h2 className="text-3xl font-extrabold text-herb-800">Start Your Wellness Journey Today</h2>
        <p className="mx-auto mt-3 max-w-xl text-herb-500">
          Join thousands of satisfied customers experiencing natural healing and building a rewarding network.
        </p>
        <Link to="/franchise" className="btn-accent mt-6 px-8 py-3 text-base">Sign Up Now</Link>
      </section>
    </div>
  );
}
