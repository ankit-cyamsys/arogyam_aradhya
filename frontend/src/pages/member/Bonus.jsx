import CommissionList from "../../components/CommissionList";

export default function Bonus() {
  return (
    <CommissionList
      kind="matching"
      title="Matching Bonus"
      emptyText="No matching bonus yet. Balance your left & right legs to earn binary matching income."
    />
  );
}
