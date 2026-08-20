import CommissionList from "../../components/CommissionList";

export default function LevelBonus() {
  return (
    <CommissionList
      kind="level"
      title="Level Bonus"
      emptyText="No level bonus yet. You earn level bonus when your sponsored downline purchases products."
    />
  );
}
