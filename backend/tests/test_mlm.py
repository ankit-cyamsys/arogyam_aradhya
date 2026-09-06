from decimal import Decimal

from app.models import CommissionLedger, WeeklyPayout
from app.services import ranks as ranks_svc
from app.services.mlm_engine import close_payout_period, compute_matching, pay_due_rank_bonuses, update_rank
from tests.conftest import make_member, buy


def _wallet(m):
    return float(m.wallet_balance or 0)


# ---------------- Activation ("greening" at 50 SP) ----------------
def test_activation_at_50_sp(db, product):
    sponsor = make_member(db, "Sponsor", active=True)
    m = make_member(db, "New", sponsor=sponsor, position="L")
    buy(db, m, product, 49)
    assert m.is_active is False, "49 SP should NOT activate"
    buy(db, m, product, 1)
    assert m.is_active is True, "50 SP total should activate (green)"


def test_direct_referral_bonus_500_on_activation(db, product):
    sponsor = make_member(db, "Sponsor", active=True)
    m = make_member(db, "New", sponsor=sponsor, position="L")
    buy(db, m, product, 50)  # activates
    db.refresh(sponsor)
    refs = db.query(CommissionLedger).filter_by(member_id=sponsor.id, kind="referral").all()
    assert len(refs) == 1 and float(refs[0].amount) == 500.0


# ---------------- Binary matching: ₹10/SP in blocks of 50 ----------------
def _seed_carry(db, member, left, right, wk_left=None, wk_right=None):
    member.left_carry = Decimal(str(left))
    member.right_carry = Decimal(str(right))
    member.week_left_sp = Decimal(str(wk_left if wk_left is not None else left))
    member.week_right_sp = Decimal(str(wk_right if wk_right is not None else right))
    db.commit()


def test_matching_50_50_pays_500(db, product):
    m = make_member(db, "M", active=True)
    _seed_carry(db, m, 50, 50)
    res = compute_matching(db, m, commit=True)
    assert res["closing_sp"] == 50.0
    assert res["payout"] == 500.0
    assert float(m.left_carry) == 0.0 and float(m.right_carry) == 0.0


def test_matching_blocks_and_carry_forward(db, product):
    m = make_member(db, "M", active=True)
    _seed_carry(db, m, 130, 130)
    res = compute_matching(db, m, commit=True)
    assert res["closing_sp"] == 100.0   # 130 -> 2 blocks of 50
    assert res["payout"] == 1000.0
    assert float(m.left_carry) == 30.0 and float(m.right_carry) == 30.0


def test_matching_below_50_pays_nothing(db, product):
    m = make_member(db, "M", active=True)
    _seed_carry(db, m, 45, 200)
    res = compute_matching(db, m, commit=True)
    assert res["closing_sp"] == 0.0 and res["payout"] == 0.0
    assert float(m.left_carry) == 45.0 and float(m.right_carry) == 200.0


# ---------------- Weekly close writes a register row ----------------
def test_weekly_close_register(db, product):
    m = make_member(db, "M", active=True)
    _seed_carry(db, m, 82.5, 45.7, wk_left=5.25, wk_right=45.70)
    summary = close_payout_period(db, "2026-W36", "28 Aug 2026")
    row = db.query(WeeklyPayout).filter_by(member_id=m.id).one()
    assert float(row.closing_sp) == 0.0   # min(82.5,45.7)=45.7 -> below 50 block
    # give both legs enough and re-close
    _seed_carry(db, m, 120, 60, wk_left=120, wk_right=60)
    close_payout_period(db, "2026-W37", "04 Sep 2026")
    row2 = db.query(WeeklyPayout).filter_by(member_id=m.id, period="2026-W37").one()
    assert float(row2.closing_sp) == 50.0 and float(row2.payout) == 500.0
    assert float(row2.cf_left) == 70.0 and float(row2.cf_right) == 10.0
    assert float(m.week_left_sp) == 0.0  # week counters reset


# ---------------- Rank detection ----------------
def test_rank_detection(db):
    ranks = ranks_svc.get_ranks(db)
    assert ranks_svc.compute_rank(ranks, 199, 500) is None          # left below 200
    assert ranks_svc.compute_rank(ranks, 200, 200)["level"] == 1     # Winner
    assert ranks_svc.compute_rank(ranks, 4000, 4000)["level"] == 5   # Master
    assert ranks_svc.compute_rank(ranks, 5000, 4000)["level"] == 5   # weaker leg governs
    assert ranks_svc.compute_rank(ranks, 500000, 500000)["level"] == 12  # Global Icon


def test_update_rank_from_totals(db):
    m = make_member(db, "M", active=True)
    m.total_left_sp = Decimal("2000")
    m.total_right_sp = Decimal("2500")
    db.commit()
    assert update_rank(db, m) == 4  # Champion (both >= 2000, right < 4000)


# ---------------- Rank bonus (admin paid, cumulative, one-time) ----------------
def test_pay_due_rank_bonuses(db):
    m = make_member(db, "M", active=True)
    m.total_left_sp = Decimal("1000")
    m.total_right_sp = Decimal("1000")
    db.commit()
    update_rank(db, m)
    assert m.rank_level == 3  # Warrior
    paid = pay_due_rank_bonuses(db, m)
    # levels 1,2,3 => 4000 + 10000 + 20000
    assert [p["level"] for p in paid] == [1, 2, 3]
    assert _wallet(m) == 34000.0
    assert m.rank_bonus_paid_level == 3
    # paying again pays nothing (one-time)
    assert pay_due_rank_bonuses(db, m) == []
    assert _wallet(m) == 34000.0


# ---------------- Direct selling: 40% commission on taxable ----------------
def test_direct_commission_40pct(db, product):
    seller = make_member(db, "Seller", segment="direct")
    buy(db, seller, product, 10)  # 10 units x ₹100 = ₹1000 taxable
    db.refresh(seller)
    dsa = db.query(CommissionLedger).filter_by(member_id=seller.id, kind="dsa").one()
    assert float(dsa.amount) == 400.0  # 40% of 1000
    assert seller.is_active is True
