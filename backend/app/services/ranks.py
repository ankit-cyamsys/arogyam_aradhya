"""Career ranks (WINNER → GLOBAL ICON).

A member's rank is auto-detected from cumulative SP on BOTH legs reaching the
threshold. The one-time rank BONUS (cash) is credited by the admin (mirrors the
reference, where rank bonuses are paid manually). `reward` is the non-cash
recognition (gift/tour) fulfilled offline.
"""
from __future__ import annotations

import json
from decimal import Decimal

from sqlalchemy.orm import Session

# level, name, tier, sp (each leg), bonus (cash ₹), reward (non-cash)
DEFAULT_RANKS = [
    {"level": 1, "name": "Winner", "tier": "STARTER", "sp": 200, "bonus": 4000, "reward": "Bag"},
    {"level": 2, "name": "Achiever", "tier": "BRONZE", "sp": 500, "bonus": 10000, "reward": "Smart Watch"},
    {"level": 3, "name": "Warrior", "tier": "BRONZE", "sp": 1000, "bonus": 20000, "reward": "Tablet"},
    {"level": 4, "name": "Champion", "tier": "SILVER", "sp": 2000, "bonus": 40000, "reward": "Jim Corbett 2N/3D"},
    {"level": 5, "name": "Master", "tier": "SILVER", "sp": 4000, "bonus": 80000, "reward": "₹15,000 Mobile + Agra Tour 2N/3D"},
    {"level": 6, "name": "Commander", "tier": "GOLD", "sp": 8000, "bonus": 80000, "reward": "₹30,000 Bike + Shimla 2N/3D with Spouse"},
    {"level": 7, "name": "Royal Executive", "tier": "GOLD", "sp": 16000, "bonus": 250000, "reward": "₹1,50,000 Laptop + Gangtok 2N/3D with Spouse"},
    {"level": 8, "name": "Imperial Leader", "tier": "PLATINUM", "sp": 32500, "bonus": 400000, "reward": "₹2,00,000 Gold + Goa 2N/3D with Spouse"},
    {"level": 9, "name": "Diamond", "tier": "PLATINUM", "sp": 65000, "bonus": 600000, "reward": "₹3,00,000 Car + Bangkok & Pattaya 2N/3D"},
    {"level": 10, "name": "Crown", "tier": "DIAMOND", "sp": 125000, "bonus": 1000000, "reward": "₹5,00,000 Car + Indonesia 3N/4D with Spouse"},
    {"level": 11, "name": "King", "tier": "DIAMOND", "sp": 250000, "bonus": 1500000, "reward": "₹7,50,000 Car + Switzerland 3N/4D with Spouse"},
    {"level": 12, "name": "Global Icon", "tier": "CROWN", "sp": 500000, "bonus": 2500000, "reward": "₹20,00,000 + Dubai with Family 4N/5D"},
]


def get_ranks(db: Session) -> list[dict]:
    from app.services import settings_service as cfg
    raw = cfg.get(db, "ranks", None)
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = None
    return raw or DEFAULT_RANKS


def compute_rank(ranks: list[dict], left_sp, right_sp) -> dict | None:
    """Highest rank whose SP threshold is met on BOTH legs (cumulative)."""
    left = Decimal(str(left_sp or 0))
    right = Decimal(str(right_sp or 0))
    achieved = None
    for r in sorted(ranks, key=lambda x: x["level"]):
        if left >= Decimal(str(r["sp"])) and right >= Decimal(str(r["sp"])):
            achieved = r
        else:
            break
    return achieved


def rank_by_level(ranks: list[dict], level: int) -> dict | None:
    for r in ranks:
        if r["level"] == level:
            return r
    return None
