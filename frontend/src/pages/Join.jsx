import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import AuthModal from "../components/AuthModal";

export default function Join() {
  const navigate = useNavigate();
  const [modal, setModal] = useState(null); // 'login' | 'signup'

  return (
    <div>
      <PageHeader
        icon="🚪"
        title="Choose Your Portal"
        subtitle="Two ways to grow with Arogyam Aradhya — pick the one that fits you."
      />
      <div className="mx-auto grid max-w-4xl gap-6 px-4 py-16 md:grid-cols-2">
        {/* MLM */}
        <div className="card flex flex-col p-8">
          <div className="mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-herb-100 text-3xl">🌳</div>
          <h2 className="text-xl font-extrabold text-herb-800">MLM Network</h2>
          <p className="mt-2 flex-1 text-sm text-herb-500">
            Build a binary team, earn matching bonus, level bonus and ₹500 per direct referral.
            Grow a wellness network and earn from both legs.
          </p>
          <ul className="my-4 space-y-1.5 text-sm text-herb-600">
            <li>✔ Binary genealogy tree</li>
            <li>✔ Matching + level + referral income</li>
            <li>✔ Weekly payouts & rank rewards</li>
          </ul>
          <div className="flex gap-2">
            <button onClick={() => setModal("signup")} className="btn-primary flex-1">Sign Up</button>
            <button onClick={() => setModal("login")} className="btn-outline flex-1">Login</button>
          </div>
        </div>

        {/* Direct Selling */}
        <div className="card flex flex-col p-8 ring-2 ring-marigold-200">
          <div className="mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-marigold-100 text-3xl">🛍️</div>
          <h2 className="text-xl font-extrabold text-herb-800">Direct Selling</h2>
          <p className="mt-2 flex-1 text-sm text-herb-500">
            Sell products directly and earn a flat <b className="text-marigold-600">40% commission</b> on
            every sale. No team required — just sell and earn.
          </p>
          <ul className="my-4 space-y-1.5 text-sm text-herb-600">
            <li>✔ Flat 40% on each sale</li>
            <li>✔ Simple, single-level</li>
            <li>✔ Instant wallet credit & payouts</li>
          </ul>
          <div className="flex gap-2">
            <button onClick={() => navigate("/seller/signup")} className="btn-accent flex-1">Sign Up</button>
            <button onClick={() => navigate("/seller/login")} className="btn-outline flex-1">Login</button>
          </div>
        </div>
      </div>
      <AuthModal open={!!modal} mode={modal || "login"} onClose={() => setModal(null)} />
    </div>
  );
}
