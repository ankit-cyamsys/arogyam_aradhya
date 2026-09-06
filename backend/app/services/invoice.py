"""Build GST invoice data from an order."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models import Member, Order
from app.services import settings_service as cfg


def _q(x) -> Decimal:
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _two(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return (_TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")).strip()


def _three(n: int) -> str:
    h, r = divmod(n, 100)
    out = (_ONES[h] + " Hundred" if h else "")
    if r:
        out += (" " if out else "") + _two(r)
    return out


def amount_in_words(amount: Decimal) -> str:
    """Indian numbering system (Lakh/Crore) rupees-and-paise in words."""
    amount = _q(amount)
    rupees = int(amount)
    paise = int((amount - rupees) * 100)
    if rupees == 0:
        words = "Zero"
    else:
        crore, rem = divmod(rupees, 10_000_000)
        lakh, rem = divmod(rem, 100_000)
        thousand, rem = divmod(rem, 1000)
        parts = []
        if crore:
            parts.append(_two(crore) + " Crore")
        if lakh:
            parts.append(_two(lakh) + " Lakh")
        if thousand:
            parts.append(_two(thousand) + " Thousand")
        if rem:
            parts.append(_three(rem))
        words = " ".join(parts)
    result = f"{words} Rupees"
    if paise:
        result += f" and {_two(paise)} Paise"
    return result + " Only"


def build_invoice(db: Session, order: Order) -> dict:
    s = cfg.get_all(db)
    gst_rate = Decimal(str(s.get("gst_rate", 18)))
    inclusive = bool(s.get("price_gst_inclusive", False))
    hsn = s.get("hsn_default", "30049011")

    buyer = db.get(Member, order.member_id)
    company_state = (s.get("company_state") or "").strip().lower()
    buyer_state = (getattr(buyer, "state", "") or "").strip().lower()
    # Same state (or unknown) => CGST + SGST; different => IGST.
    intra = (not buyer_state) or (buyer_state == company_state)

    items = []
    taxable_total = Decimal("0")
    for it in order.items:
        line_gross = Decimal(str(it.price)) * it.quantity
        if inclusive:
            taxable = (line_gross / (Decimal("1") + gst_rate / 100))
        else:
            taxable = line_gross
        taxable = _q(taxable)
        gst_amt = _q(taxable * gst_rate / 100)
        taxable_total += taxable
        items.append({
            "name": it.name,
            "hsn": hsn,
            "qty": it.quantity,
            "rate": float(_q(taxable / it.quantity if it.quantity else taxable)),
            "taxable": float(taxable),
            "gst_rate": float(gst_rate),
            "cgst": float(_q(gst_amt / 2)) if intra else 0.0,
            "sgst": float(_q(gst_amt / 2)) if intra else 0.0,
            "igst": 0.0 if intra else float(gst_amt),
            "total": float(_q(taxable + gst_amt)),
        })

    taxable_total = _q(taxable_total)
    gst_total = _q(taxable_total * gst_rate / 100)
    grand = _q(taxable_total + gst_total)
    half = _q(gst_total / 2)

    return {
        "invoice_no": f"{s.get('invoice_prefix', 'INV')}-{order.order_no}",
        "date": order.created_at.date().isoformat() if order.created_at else None,
        "seller": {
            "name": s.get("company_legal_name", "Arogyam Aradhya Herbs"),
            "gstin": s.get("gstin", ""),
            "address": s.get("company_address", ""),
            "state": s.get("company_state", ""),
            "state_code": s.get("company_state_code", ""),
            "phone": s.get("support_phone", ""),
            "email": s.get("support_email", ""),
        },
        "buyer": {
            "name": buyer.name if buyer else "",
            "member_id": buyer.member_id if buyer else "",
            "phone": buyer.phone if buyer else "",
            "address": ", ".join(filter(None, [
                getattr(buyer, "address", None), getattr(buyer, "city", None),
                getattr(buyer, "state", None), getattr(buyer, "pincode", None),
            ])) if buyer else "",
            "state": getattr(buyer, "state", "") if buyer else "",
        },
        "intra_state": intra,
        "items": items,
        "totals": {
            "taxable": float(taxable_total),
            "cgst": float(half) if intra else 0.0,
            "sgst": float(half) if intra else 0.0,
            "igst": 0.0 if intra else float(gst_total),
            "gst_total": float(gst_total),
            "grand_total": float(grand),
            "in_words": amount_in_words(grand),
        },
    }
