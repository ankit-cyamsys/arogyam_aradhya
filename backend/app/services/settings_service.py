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
    "matching_per_sp": (10.0, "₹ per matched SP (1 SP : 1 SP = ₹10 → 50 SP = ₹500)", "matching"),
    "matching_block_sp": (50.0, "Matching pays in blocks of this many SP (min 50)", "matching"),
    "matching_ratio": ("1:1", "Left:Right matching ratio", "matching"),
    # Weekly matching capping tiers by the member's first (greening) purchase SP.
    "capping_25sp": (50000.0, "Weekly matching cap (₹) if first purchase ≥25 SP", "matching"),
    "capping_50sp": (100000.0, "Weekly matching cap (₹) if first purchase ≥50 SP", "matching"),
    "capping_100sp": (200000.0, "Weekly matching cap (₹) if first purchase ≥100 SP", "matching"),
    # ---- Direct-selling platform (DSA) ----
    "dsa_percent": (40.0, "Direct-seller (DSA) commission % of sale (on taxable value)", "direct"),
    # ---- GST / Invoicing ----
    "gst_rate": (5.0, "GST rate % on products", "gst"),
    "price_gst_inclusive": (False, "Are DP/MRP prices GST-inclusive?", "gst"),
    "company_legal_name": ("Arogyam Aradhya Herbs", "Legal business name on invoice", "gst"),
    "gstin": ("09EJFPP4671A1Z5", "Company GSTIN", "gst"),
    "company_address": ("Varanasi, Uttar Pradesh", "Company address on invoice", "gst"),
    "company_state": ("Uttar Pradesh", "Company state (place of supply)", "gst"),
    "company_state_code": ("09", "GST state code (UP = 09)", "gst"),
    "hsn_default": ("30049011", "Default HSN/SAC code for products", "gst"),
    "invoice_prefix": ("INV", "Invoice number prefix", "gst"),
    # ---- Activation / eligibility ----
    "activation_sp": (25.0, "Self-purchase SP (cumulative) to green an ID", "eligibility"),
    # ---- Payout ----
    "payout_min": (500.0, "Minimum wallet balance to request payout (₹)", "payout"),
    "tds_percent": (5.0, "TDS deduction on payout %", "payout"),
    "payout_day": ("Tuesday", "Weekly payout closing day", "payout"),
    # ---- Site ----
    "company_name": ("Arogyam Aradhya", "Company name", "site"),
    "support_phone": ("+91 00000 00000", "Support phone", "site"),
    "support_email": ("support@arogyamaradhya.com", "Support email", "site"),
    "address": ("Varanasi, Uttar Pradesh", "Company address", "site"),
    "whatsapp_number": ("919839227978", "Company WhatsApp number (orders)", "site"),
    "whatsapp_message": (
        "Welcome to Arogyam Aradhya! Here is my order detail and invoice. "
        "Please guide me for payment to the Admin account so I get all benefits.",
        "WhatsApp order intro message", "site",
    ),
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
