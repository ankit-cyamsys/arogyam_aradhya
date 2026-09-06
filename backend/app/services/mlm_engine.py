"""The configurable binary MLM commission engine.

Flow when an order is placed & paid:
  1. Record self-purchase SP on the buyer; activate if threshold met.
  2. Propagate the order SP up every ancestor's matching leg (L/R).
  3. Pay the sponsor line a multi-level "level bonus".
Matching payout itself is computed on demand / at period close via
`compute_matching` so left vs right can accumulate independently and
carry forward, exactly like the reference dashboard.
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Member, Order, SPLedger, CommissionLedger
from app.services import settings_service as cfg
from app.services import tree


def _d(x) -> Decimal:
    return Decimal(str(x or 0))


def process_order(db: Session, order: Order) -> None:
    """Route a paid order to the correct commission engine by member segment."""
    buyer = db.get(Member, order.member_id)
    if buyer is None:
        return
    if buyer.segment == "direct":
        process_direct_order(db, buyer, order)
    else:
        process_mlm_order(db, buyer, order)


def process_direct_order(db: Session, buyer: Member, order: Order) -> None:
    """Direct seller earns a flat DSA % on their own sale. No tree, no SP.

    Commission is on the taxable value (DP), not the GST-inclusive grand total.
    """
    dsa_pct = _d(cfg.get(db, "dsa_percent", 40))
    commission = (_d(order.subtotal) * dsa_pct / _d(100)).quantize(Decimal("0.01"))
    if commission > 0:
        db.add(CommissionLedger(member_id=buyer.id, kind="dsa", amount=commission,
                                note=f"{dsa_pct}% on {order.order_no}"))
        buyer.wallet_balance = _d(buyer.wallet_balance) + commission
        buyer.total_earned = _d(buyer.total_earned) + commission
    if not buyer.is_active:
        buyer.is_active = True
        from app.models.base import utcnow
        buyer.activated_at = utcnow()
    db.commit()


def process_mlm_order(db: Session, buyer: Member, order: Order) -> None:
    """Apply SP propagation + level bonus + activation for a paid MLM order."""
    order_sp = _d(order.total_sp)

    # 1. Self purchase + activation
    buyer.self_purchase_sp = _d(buyer.self_purchase_sp) + order_sp
    db.add(SPLedger(member_id=buyer.id, source_member_id=buyer.id, order_id=order.id,
                    leg="S", sp=order_sp, note="Self purchase"))
    activation_sp = _d(cfg.get(db, "activation_sp", 50))  # "greening" at 50 SP
    if not buyer.is_active and _d(buyer.self_purchase_sp) >= activation_sp:
        buyer.is_active = True
        from app.models.base import utcnow
        buyer.activated_at = utcnow()
        _pay_direct_referral(db, buyer, order)

    # 2. Propagate SP up the binary tree. Matching is settled at the WEEKLY close
    #    (see close_payout_period), so per order we only accrue SP and refresh rank.
    for ancestor, leg in tree.ancestors_with_leg(db, buyer):
        if leg == "L":
            ancestor.left_carry = _d(ancestor.left_carry) + order_sp
            ancestor.total_left_sp = _d(ancestor.total_left_sp) + order_sp
            ancestor.week_left_sp = _d(ancestor.week_left_sp) + order_sp
        else:
            ancestor.right_carry = _d(ancestor.right_carry) + order_sp
            ancestor.total_right_sp = _d(ancestor.total_right_sp) + order_sp
            ancestor.week_right_sp = _d(ancestor.week_right_sp) + order_sp
        db.add(SPLedger(member_id=ancestor.id, source_member_id=buyer.id, order_id=order.id,
                        leg=leg, sp=order_sp, note=f"Downline {buyer.member_id}"))
        update_rank(db, ancestor)

    update_rank(db, buyer)
    db.commit()


def update_rank(db: Session, member: Member) -> int:
    """Refresh a member's displayed rank from cumulative L/R SP. Returns rank level."""
    from app.services import ranks as ranks_svc
    r = ranks_svc.compute_rank(ranks_svc.get_ranks(db), member.total_left_sp, member.total_right_sp)
    level = r["level"] if r else 0
    if level != member.rank_level:
        member.rank_level = level
    return level


def _pay_direct_referral(db: Session, buyer: Member, order: Order) -> None:
    """One-time direct-referral bonus (₹500) to the sponsor when an ID activates."""
    if buyer.sponsor_id is None:
        return
    sponsor = db.get(Member, buyer.sponsor_id)
    if sponsor is None:
        return
    bonus = _d(cfg.get(db, "direct_referral_bonus", 500))
    if bonus <= 0:
        return
    db.add(CommissionLedger(member_id=sponsor.id, kind="referral", amount=bonus,
                            note=f"Direct referral: {buyer.member_id}"))
    sponsor.wallet_balance = _d(sponsor.wallet_balance) + bonus
    sponsor.total_earned = _d(sponsor.total_earned) + bonus


def _pay_level_bonus(db: Session, buyer: Member, order: Order) -> None:
    percents = cfg.get(db, "level_bonus_percent", [10, 5, 3, 2, 1]) or []
    order_value = _d(order.total)
    node = buyer
    for level, pct in enumerate(percents):
        if node.sponsor_id is None:
            break
        sponsor = db.get(Member, node.sponsor_id)
        if sponsor is None:
            break
        if sponsor.is_active:
            amount = (order_value * _d(pct) / _d(100)).quantize(Decimal("0.01"))
            if amount > 0:
                db.add(CommissionLedger(member_id=sponsor.id, kind="level", amount=amount,
                                        note=f"L{level + 1} on {order.order_no}"))
                sponsor.wallet_balance = _d(sponsor.wallet_balance) + amount
                sponsor.total_earned = _d(sponsor.total_earned) + amount
        node = sponsor


def compute_matching(db: Session, member: Member, commit: bool = True) -> dict:
    """Match left vs right carry-forward SP and pay the matching bonus.

    Returns the matched SP, payout, and leftover carry per leg.
    """
    left = _d(member.left_carry)
    right = _d(member.right_carry)
    matched = min(left, right)

    # Plan: ₹10 per matched SP, paid only in blocks of 50 SP (50 SP = ₹500).
    # The unmatched remainder carries forward. Matches the reference payout register.
    per_sp = _d(cfg.get(db, "matching_per_sp", 10))
    block = _d(cfg.get(db, "matching_block_sp", 50))
    capping = _d(cfg.get(db, "daily_capping", 0))

    if block > 0:
        closing = (matched // block) * block   # largest multiple of 50 <= matched
    else:
        closing = matched
    gross = (closing * per_sp).quantize(Decimal("0.01"))
    payout = min(gross, capping) if capping > 0 else gross

    result = {
        "matched_sp": float(matched),
        "closing_sp": float(closing),
        "left_carry_before": float(left),
        "right_carry_before": float(right),
        "gross": float(gross),
        "payout": float(payout),
        "capped": float(max(gross - payout, 0)),
    }

    if closing > 0:
        member.left_carry = left - closing
        member.right_carry = right - closing
        db.add(CommissionLedger(member_id=member.id, kind="matching", amount=payout,
                                sp_matched=closing, note="Binary matching"))
        member.wallet_balance = _d(member.wallet_balance) + payout
        member.total_earned = _d(member.total_earned) + payout
        result["left_carry_after"] = float(member.left_carry)
        result["right_carry_after"] = float(member.right_carry)

    if commit:
        db.commit()

    return result


def close_payout_period(db: Session, period: str, week_label: str | None = None) -> dict:
    """Weekly close: match every member's carry (₹10/SP in 50-blocks) and write
    one payout-register row per member who had activity. Returns a summary.
    """
    from sqlalchemy import select
    from app.models import WeeklyPayout

    per_sp = _d(cfg.get(db, "matching_per_sp", 10))
    block = _d(cfg.get(db, "matching_block_sp", 50))
    capping = _d(cfg.get(db, "daily_capping", 0))

    members = db.execute(select(Member).where(Member.segment == "mlm")).scalars().all()
    rows = 0
    total_paid = Decimal("0")
    for m in members:
        left = _d(m.left_carry)
        right = _d(m.right_carry)
        wk_left = _d(m.week_left_sp)
        wk_right = _d(m.week_right_sp)
        matched = min(left, right)
        closing = (matched // block) * block if block > 0 else matched
        gross = (closing * per_sp).quantize(Decimal("0.01"))
        payout = min(gross, capping) if capping > 0 else gross

        # Skip members with no activity and nothing to pay this period.
        if wk_left == 0 and wk_right == 0 and closing == 0:
            continue

        if closing > 0:
            m.left_carry = left - closing
            m.right_carry = right - closing
            m.wallet_balance = _d(m.wallet_balance) + payout
            m.total_earned = _d(m.total_earned) + payout
            db.add(CommissionLedger(member_id=m.id, kind="matching", amount=payout,
                                    sp_matched=closing, period=period, note=f"Weekly matching {period}"))
            total_paid += payout

        db.add(WeeklyPayout(
            member_id=m.id, period=period, week_label=week_label or period,
            left_sp=wk_left, right_sp=wk_right, matching_sp=matched, closing_sp=closing,
            payout=payout, cf_left=m.left_carry, cf_right=m.right_carry, status="paid",
        ))
        rows += 1
        m.week_left_sp = Decimal("0")
        m.week_right_sp = Decimal("0")

    db.commit()
    return {"period": period, "rows": rows, "total_paid": float(total_paid)}


def pay_due_rank_bonuses(db: Session, member: Member) -> list[dict]:
    """Admin action: pay all achieved-but-unpaid one-time rank bonuses to a member.

    Mirrors the reference where rank bonuses are paid manually from admin.
    """
    from app.services import ranks as ranks_svc

    ranks = ranks_svc.get_ranks(db)
    update_rank(db, member)  # ensure rank_level is current
    paid = []
    for lvl in range(int(member.rank_bonus_paid_level) + 1, int(member.rank_level) + 1):
        r = ranks_svc.rank_by_level(ranks, lvl)
        if not r:
            continue
        amount = _d(r.get("bonus", 0))
        if amount > 0:
            db.add(CommissionLedger(member_id=member.id, kind="rank", amount=amount,
                                    note=f"Rank bonus: {r['name']} ({r['sp']}:{r['sp']} SP)"))
            member.wallet_balance = _d(member.wallet_balance) + amount
            member.total_earned = _d(member.total_earned) + amount
        member.rank_bonus_paid_level = lvl
        paid.append({"level": lvl, "name": r["name"], "bonus": float(amount), "reward": r.get("reward")})
    db.commit()
    return paid
