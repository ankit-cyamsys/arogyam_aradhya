import CommissionList from "../../components/CommissionList";

export default function SellerEarnings() {
  return (
    <CommissionList
      kind="dsa"
      title="My Earnings"
      emptyText="No earnings yet. Sell your first product to earn 40% commission instantly."
    />
  );
}
