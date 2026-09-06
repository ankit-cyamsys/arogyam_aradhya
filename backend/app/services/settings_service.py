"""Admin-configurable MLM & site settings.

All commission parameters live here as DB rows so the business owner can tune
them from the admin panel without code changes. Defaults are sensible
placeholders for a binary plan and MUST be reviewed before going live.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Setting

# key -> (default_value, label, group)
DEFAULTS: dict[str, tuple[Any, str, str]] = {
    # ---- Binary matching (MLM) ----
    "matching_per_sp": (15.0, "₹ per matched SP (₹1,500 per 100:100 → 50:50 = ₹750)", "matching"),
    "matching_ratio": ("1:1", "Left:Right matching ratio", "matching"),
    "daily_capping": (0.0, "Max matching payout per member per period (₹, 0 = no cap)", "matching"),
    "direct_referral_bonus": (500.0, "One-time bonus per direct referral (₹)", "matching"),
    # ---- Start Level Bonus (one-time) ----
    "start_bonus_sp": (200.0, "SP needed on EACH leg for the start bonus", "start"),
    "start_bonus_amount": (3000.0, "Start Level Bonus amount (₹) at 200:200 SP", "start"),
    # ---- Level / referral bonus (index 0 = level 1 = direct sponsor) ----
    "level_bonus_percent": (
        json.dumps([10, 5, 3, 2, 1]),
        "Level bonus % of order value by depth (direct, 2nd, 3rd...)",
        "level",
    ),
    # ---- Direct-selling platform (DSA) ----
    "dsa_percent": (40.0, "Direct-seller (DSA) commission % of sale", "direct"),
    "mgmt_percent": (25.0, "Management share % of sale", "direct"),
    "company_profit_percent": (35.0, "Company profit share % of sale", "direct"),
    # ---- Plan economics (reference / guardrails) ----
    "product_cost_percent": (36.0, "Product cost (COGS) as % of turnover", "economics"),
    "payout_min_percent": (18.0, "Total network payout floor (% of turnover)", "economics"),
    "payout_max_percent": (22.0, "Total network payout ceiling (% of turnover)", "economics"),
    # ---- Activation / eligibility ----
    "activation_sp": (50.0, "Self-purchase SP to activate/green an ID", "eligibility"),
    "repurchase_sp": (25.0, "Monthly repurchase SP to stay active", "eligibility"),
    # ---- Payout ----
    "payout_min": (500.0, "Minimum wallet balance to request payout (₹)", "payout"),
    "admin_charge_percent": (5.0, "Admin/processing charge on payout %", "payout"),
    "tds_percent": (5.0, "TDS deduction on payout %", "payout"),
    "payout_day": ("Monday", "Weekly payout closing day", "payout"),
    # ---- Site ----
    "company_name": ("Arogyam Aradhya", "Company name", "site"),
    "support_phone": ("+91 00000 00000", "Support phone", "site"),
    "support_email": ("support@arogyamaradhya.com", "Support email", "site"),
    "address": ("Varanasi, Uttar Pradesh", "Company address", "site"),
}


def _coerce(raw: str) -> Any:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def seed_defaults(db: Session) -> None:
    existing = {s.key for s in db.execute(select(Setting)).scalars()}
    for key, (val, label, group) in DEFAULTS.items():
        if key in existing:
            continue
        stored = val if isinstance(val, str) else json.dumps(val)
        db.add(Setting(key=key, value=stored, label=label, group=group))
    db.commit()


def get_all(db: Session) -> dict[str, Any]:
    rows = db.execute(select(Setting)).scalars().all()
    out = {r.key: _coerce(r.value) for r in rows}
    # ensure defaults present even if not seeded
    for key, (val, _, _) in DEFAULTS.items():
        out.setdefault(key, val)
    return out


def get(db: Session, key: str, default: Any = None) -> Any:
    row = db.get(Setting, key)
    if row is None:
        d = DEFAULTS.get(key)
        return d[0] if d else default
    return _coerce(row.value)


def set_value(db: Session, key: str, value: Any) -> Setting:
    stored = value if isinstance(value, str) else json.dumps(value)
    row = db.get(Setting, key)
    if row is None:
        meta = DEFAULTS.get(key, (None, None, "custom"))
        row = Setting(key=key, value=stored, label=meta[1], group=meta[2])
        db.add(row)
    else:
        row.value = stored
    db.commit()
    return row
