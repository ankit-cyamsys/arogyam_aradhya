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

    # 2. Propagate SP up the binary tree, then settle each ancestor in real time
    for ancestor, leg in tree.ancestors_with_leg(db, buyer):
        if leg == "L":
            ancestor.left_carry = _d(ancestor.left_carry) + order_sp
            ancestor.total_left_sp = _d(ancestor.total_left_sp) + order_sp
        else:
            ancestor.right_carry = _d(ancestor.right_carry) + order_sp
            ancestor.total_right_sp = _d(ancestor.total_right_sp) + order_sp
        db.add(SPLedger(member_id=ancestor.id, source_member_id=buyer.id, order_id=order.id,
                        leg=leg, sp=order_sp, note=f"Downline {buyer.member_id}"))
        # Binary matching pays the parent as soon as both legs have volume
        # (e.g. 50:50 => ₹750). Runs per order so payouts are immediate.
        compute_matching(db, ancestor, commit=False)
        _pay_start_bonus(db, ancestor)

    # 3. Level (sponsor line) bonus
    _pay_level_bonus(db, buyer, order)

    db.commit()


def _pay_start_bonus(db: Session, member: Member) -> None:
    """One-time Start Level Bonus: 200 SP Left + 200 SP Right => ₹3,000."""
    if member.start_bonus_paid:
        return
    need = _d(cfg.get(db, "start_bonus_sp", 200))
    if _d(member.total_left_sp) >= need and _d(member.total_right_sp) >= need:
        amount = _d(cfg.get(db, "start_bonus_amount", 3000))
        member.start_bonus_paid = True
        if amount > 0:
            db.add(CommissionLedger(member_id=member.id, kind="start", amount=amount,
                                    note=f"Start bonus ({int(need)}:{int(need)} SP)"))
            member.wallet_balance = _d(member.wallet_balance) + amount
            member.total_earned = _d(member.total_earned) + amount


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

    # Plan: ₹1,500 per 100 SP : 100 SP  ==>  ₹15 per matched SP  (50:50 = ₹750)
    per_sp = _d(cfg.get(db, "matching_per_sp", 15))
    capping = _d(cfg.get(db, "daily_capping", 25000))

    gross = (matched * per_sp).quantize(Decimal("0.01"))
    payout = min(gross, capping) if capping > 0 else gross

    result = {
        "matched_sp": float(matched),
        "left_carry_before": float(left),
        "right_carry_before": float(right),
        "gross": float(gross),
        "payout": float(payout),
        "capped": float(max(gross - payout, 0)),
    }

    if matched > 0:
        member.left_carry = left - matched
        member.right_carry = right - matched
        db.add(CommissionLedger(member_id=member.id, kind="matching", amount=payout,
                                sp_matched=matched, note="Binary matching"))
        member.wallet_balance = _d(member.wallet_balance) + payout
        member.total_earned = _d(member.total_earned) + payout
        result["left_carry_after"] = float(member.left_carry)
        result["right_carry_after"] = float(member.right_carry)

    if commit:
        db.commit()

    return result
