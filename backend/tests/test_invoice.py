from decimal import Decimal

from app.services.invoice import build_invoice, amount_in_words
from tests.conftest import make_member, buy


def test_invoice_gst_exclusive_18pct(db, product):
    seller = make_member(db, "Seller", segment="direct")
    seller.state = "Uttar Pradesh"
    db.commit()
    o = buy(db, seller, product, 10)  # 10 x ₹100 = ₹1000 taxable
    # order total should be taxable + 18% GST
    assert float(o.subtotal) == 1000.0
    assert float(o.total) == 1180.0

    inv = build_invoice(db, o)
    t = inv["totals"]
    assert t["taxable"] == 1000.0
    assert t["cgst"] == 90.0 and t["sgst"] == 90.0   # intra-state (same as company UP)
    assert t["igst"] == 0.0
    assert t["grand_total"] == 1180.0
    assert inv["intra_state"] is True


def test_invoice_interstate_igst(db, product):
    seller = make_member(db, "Seller", segment="direct")
    seller.state = "Maharashtra"   # different from company (UP)
    db.commit()
    o = buy(db, seller, product, 5)   # ₹500 taxable
    inv = build_invoice(db, o)
    t = inv["totals"]
    assert t["igst"] == 90.0 and t["cgst"] == 0.0 and t["sgst"] == 0.0
    assert t["grand_total"] == 590.0
    assert inv["intra_state"] is False


def test_amount_in_words():
    assert amount_in_words(Decimal("1180.00")).startswith("One Thousand One Hundred Eighty Rupees")
    assert "Paise" in amount_in_words(Decimal("873.20"))
