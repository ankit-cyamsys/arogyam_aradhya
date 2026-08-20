"""Binary tree placement & genealogy helpers."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Member


def find_placement(db: Session, parent: Member, preferred: str) -> tuple[Member, str]:
    """Find the first open slot on `preferred` ('L'/'R') leg under `parent`.

    Walks down the chosen leg (outer-leg spillover) until an empty child slot
    is found, mirroring how most binary plans auto-place spillover downline.
    """
    preferred = preferred if preferred in ("L", "R") else "L"
    node = parent
    while True:
        child = _child(db, node, preferred)
        if child is None:
            return node, preferred
        node = child


def _child(db: Session, parent: Member, position: str) -> Member | None:
    return db.execute(
        select(Member).where(Member.parent_id == parent.id, Member.position == position)
    ).scalar_one_or_none()


def children(db: Session, member: Member) -> dict[str, Member | None]:
    return {"L": _child(db, member, "L"), "R": _child(db, member, "R")}


def ancestors_with_leg(db: Session, member: Member) -> list[tuple[Member, str]]:
    """Return [(ancestor, leg_the_member_falls_on), ...] from parent up to root.

    `leg` is 'L' or 'R': the side of the ancestor whose subtree contains
    `member`. Used to credit SP up both legs.
    """
    chain: list[tuple[Member, str]] = []
    node = member
    guard = 0
    while node.parent_id is not None and guard < 200:
        parent = db.get(Member, node.parent_id)
        if parent is None:
            break
        chain.append((parent, node.position or "L"))
        node = parent
        guard += 1
    return chain


def subtree_counts(db: Session, member: Member) -> dict[str, int]:
    """Count members on each leg (active + total) via BFS."""
    out = {"left": 0, "right": 0, "left_active": 0, "right_active": 0}
    for leg, key in (("L", "left"), ("R", "right")):
        root = _child(db, member, leg)
        if root is None:
            continue
        stack = [root]
        while stack:
            n = stack.pop()
            out[key] += 1
            if n.is_active:
                out[f"{key}_active"] += 1
            kids = children(db, n)
            stack.extend([c for c in kids.values() if c is not None])
    return out


def build_tree(db: Session, member: Member, depth: int = 3) -> dict:
    """Serialize the genealogy tree to `depth` levels for the UI."""

    def node(m: Member | None, d: int) -> dict | None:
        if m is None:
            return None
        data = {
            "member_id": m.member_id,
            "name": m.name,
            "is_active": m.is_active,
            "position": m.position,
            "left": None,
            "right": None,
        }
        if d > 0:
            kids = children(db, m)
            data["left"] = node(kids["L"], d - 1)
            data["right"] = node(kids["R"], d - 1)
        return data

    return node(member, depth)
