import { Link } from "react-router-dom";
import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="mt-20 bg-herb-900 text-herb-100">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <Logo light />
          <p className="mt-4 max-w-xs text-sm text-herb-200">
            Your trusted partner for authentic Ayurvedic medicines, natural healing and a rewarding
            wellness network.
          </p>
        </div>
        <div>
          <h4 className="mb-3 font-semibold text-white">Quick Links</h4>
          <ul className="space-y-2 text-sm">
            {[["Home", "/"], ["Products", "/products"], ["Franchise", "/franchise"], ["Documents", "/documents"], ["About Us", "/about"], ["Contact", "/contact"]].map(([l, t]) => (
              <li key={t}>
                <Link to={t} className="text-herb-200 hover:text-white">{l}</Link>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="mb-3 font-semibold text-white">Categories</h4>
          <ul className="space-y-2 text-sm text-herb-200">
            <li>Immunity Boosters</li>
            <li>Digestive Health</li>
            <li>Skin Care</li>
            <li>General Wellness</li>
          </ul>
        </div>
        <div>
          <h4 className="mb-3 font-semibold text-white">Contact Info</h4>
          <ul className="space-y-2 text-sm text-herb-200">
            <li>📞 +91 00000 00000</li>
            <li>✉️ support@arogyamaradhya.com</li>
            <li>📍 Varanasi, Uttar Pradesh</li>
            <li>🕒 Mon–Sat: 9AM–6PM</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-herb-800 py-4 text-center text-xs text-herb-300">
        © {new Date().getFullYear()} Arogyam Aradhya. All rights reserved. · Made with 🌿 for natural healing
        · <Link to="/join" className="hover:text-white">Join</Link>
        · <Link to="/seller/login" className="hover:text-white">Seller Login</Link>
        · <Link to="/admin/login" className="hover:text-white">Admin</Link>
      </div>
    </footer>
  );
}
