from decimal import Decimal

from app.models import CommissionLedger, WeeklyPayout
from app.services import ranks as ranks_svc
from app.services.mlm_engine import close_payout_period, compute_matching, pay_due_rank_bonuses, update_rank
from tests.conftest import make_member, buy


def _wallet(m):
    return float(m.wallet_balance or 0)


# ---------------- Greening at 25 SP + capping from first purchase ----------------
def test_greening_at_25_sp(db, product):
    sponsor = make_member(db, "Sponsor", active=True)
    m = make_member(db, "New", sponsor=sponsor, position="L")
    buy(db, m, product, 24)
    assert m.is_active is False, "24 SP should NOT green"
    buy(db, m, product, 1)
    assert m.is_active is True, "25 SP total should green the ID"


def test_no_direct_referral_bonus(db, product):
    sponsor = make_member(db, "Sponsor", active=True)
    m = make_member(db, "New", sponsor=sponsor, position="L")
    buy(db, m, product, 25)  # greens — but there is NO direct-referral bonus anymore
    db.refresh(sponsor)
    assert db.query(CommissionLedger).filter_by(kind="referral").count() == 0


def test_capping_set_by_first_purchase(db, product):
    for first_sp, expected_cap in [(25, 50000), (50, 100000), (100, 200000), (150, 200000)]:
        m = make_member(db, f"M{first_sp}")
        buy(db, m, product, first_sp)
        db.refresh(m)
        assert m.is_active is True
        assert float(m.capping_limit) == expected_cap, f"{first_sp} SP → cap {expected_cap}"


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


def test_update_rank_from_matched_sp(db):
    m = make_member(db, "M", active=True)
    m.total_matched_sp = Decimal("2500")   # rank is driven by MATCHED SP
    db.commit()
    assert update_rank(db, m) == 4  # Champion (>=2000, <4000)


# ---------------- Rank bonus (admin paid, green-gated, one-time) ----------------
def test_pay_due_rank_bonuses(db):
    m = make_member(db, "M", active=True)
    m.total_matched_sp = Decimal("1000")   # matched SP → Warrior (level 3)
    db.commit()
    update_rank(db, m)
    assert m.rank_level == 3
    paid = pay_due_rank_bonuses(db, m)
    assert [p["level"] for p in paid] == [1, 2, 3]      # 4000 + 10000 + 20000
    assert _wallet(m) == 34000.0
    assert m.rank_bonus_paid_level == 3
    assert pay_due_rank_bonuses(db, m) == []            # one-time
    assert _wallet(m) == 34000.0


def test_rank_bonus_blocked_when_red(db):
    m = make_member(db, "Red", active=False)   # NOT green
    m.total_matched_sp = Decimal("1000")
    db.commit()
    assert pay_due_rank_bonuses(db, m) == []   # green gate: no bonus while red
    assert _wallet(m) == 0.0


# ---------------- Green gate + capping on weekly close ----------------
def test_weekly_close_skips_red_members(db):
    red = make_member(db, "Red", active=False)
    _seed_carry(db, red, 100, 100)
    close_payout_period(db, "2026-W40", "Wk40")
    db.refresh(red)
    assert _wallet(red) == 0.0                  # red earns nothing
    assert float(red.left_carry) == 100.0       # SP retained for when they green


def test_weekly_capping_limits_payout(db):
    m = make_member(db, "Cap", active=True)
    m.capping_limit = Decimal("50000")          # weekly cap ₹50,000 → max 5000 SP
    _seed_carry(db, m, 8000, 8000)
    close_payout_period(db, "2026-W41", "Wk41")
    db.refresh(m)
    row = db.query(WeeklyPayout).filter_by(member_id=m.id, period="2026-W41").one()
    assert float(row.closing_sp) == 5000.0 and float(row.payout) == 50000.0
    assert float(row.cf_left) == 3000.0 and float(row.cf_right) == 3000.0  # excess carries


# ---------------- Direct selling: 40% commission on taxable ----------------
def test_direct_commission_40pct(db, product):
    seller = make_member(db, "Seller", segment="direct")
    buy(db, seller, product, 10)  # 10 units x ₹100 = ₹1000 taxable
    db.refresh(seller)
    dsa = db.query(CommissionLedger).filter_by(member_id=seller.id, kind="dsa").one()
    assert float(dsa.amount) == 400.0  # 40% of 1000
    assert seller.is_active is True
