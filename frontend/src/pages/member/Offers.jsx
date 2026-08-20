const OFFERS = [
  ["🎉", "Welcome Bonus", "Activate your ID within 7 days and get bonus SP on your first purchase."],
  ["🔥", "Weekend Sale", "Flat discounts on selected wellness products every weekend."],
  ["🏅", "Rank Rewards", "Achieve new ranks in your network to unlock cash rewards & gifts."],
  ["👥", "Refer & Earn", "Extra level bonus for every active member you personally sponsor."],
];

export default function Offers() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-herb-800">Offers</h1>
        <p className="text-herb-500">Ongoing promotions and reward programs for members.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {OFFERS.map(([icon, title, text]) => (
          <div key={title} className="card flex gap-4 p-6">
            <div className="text-4xl">{icon}</div>
            <div>
              <h3 className="font-bold text-herb-800">{title}</h3>
              <p className="mt-1 text-sm text-herb-500">{text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
