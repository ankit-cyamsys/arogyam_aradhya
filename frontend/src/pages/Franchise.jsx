import { useState } from "react";
import PageHeader from "../components/PageHeader";
import AuthModal from "../components/AuthModal";

const PERKS = [
  ["💰", "Binary Matching Bonus", "Earn on every matched pair of Selling Points across your left and right legs."],
  ["🏆", "Level Bonus", "Get rewarded on the purchases of your directly sponsored downline, level by level."],
  ["🔁", "Carry Forward", "Unmatched business is never lost — it carries forward to the next cycle."],
  ["🎁", "Rewards & Offers", "Unlock exclusive member discounts, reward products and rank incentives."],
  ["📈", "Capping Protection", "Fair earnings with transparent weekly payout and capping limits."],
  ["🪪", "Digital ID Card", "Get your official distributor ID card the moment you join."],
];

const STEPS = [
  ["Join with a Sponsor", "Sign up using your sponsor's member ID and pick your leg (left/right)."],
  ["Activate your ID", "Make your first self-purchase to activate and become eligible for income."],
  ["Build your team", "Introduce members on both legs and grow your binary network."],
  ["Earn & Withdraw", "Accumulate SP, earn bonuses and request payouts to your bank."],
];

export default function Franchise() {
  const [modal, setModal] = useState(false);
  return (
    <div>
      <PageHeader icon="🤝" title="Become a Franchise Partner" subtitle="Turn wellness into a rewarding business with our transparent binary rewards plan." />
      <div className="mx-auto max-w-7xl px-4 py-16">
        <div className="grid gap-6 md:grid-cols-3">
          {PERKS.map(([icon, title, text]) => (
            <div key={title} className="card p-6">
              <div className="mb-3 text-3xl">{icon}</div>
              <h3 className="mb-1 font-bold text-herb-800">{title}</h3>
              <p className="text-sm text-herb-500">{text}</p>
            </div>
          ))}
        </div>

        <h2 className="mb-8 mt-16 text-center text-2xl font-bold text-herb-800">How to Get Started</h2>
        <div className="grid gap-6 md:grid-cols-4">
          {STEPS.map(([title, text], i) => (
            <div key={title} className="card relative p-6 pt-8">
              <div className="absolute -top-4 left-6 grid h-8 w-8 place-items-center rounded-full bg-marigold-500 font-bold text-white">{i + 1}</div>
              <h3 className="mb-1 font-bold text-herb-800">{title}</h3>
              <p className="text-sm text-herb-500">{text}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 rounded-3xl hero-gradient p-10 text-center text-white">
          <h2 className="text-2xl font-extrabold">Ready to build your wellness network?</h2>
          <p className="mx-auto mt-2 max-w-xl text-herb-100">Join today and start earning while helping others heal naturally.</p>
          <button onClick={() => setModal(true)} className="btn-accent mt-6 px-8 py-3 text-base">Join the Network</button>
        </div>
      </div>
      <AuthModal open={modal} mode="signup" onClose={() => setModal(false)} />
    </div>
  );
}
