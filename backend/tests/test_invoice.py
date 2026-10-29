from decimal import Decimal

from app.services.invoice import build_invoice, amount_in_words
from tests.conftest import make_member, buy


def test_invoice_gst_inclusive_5pct(db, product):
    seller = make_member(db, "Seller", segment="direct")
    seller.state = "Uttar Pradesh"
    db.commit()
    o = buy(db, seller, product, 10)  # 10 x ₹100 = ₹1000, GST-inclusive (DP already includes 5% GST)
    assert float(o.subtotal) == 1000.0
    assert float(o.total) == 1000.0

    inv = build_invoice(db, o)
    t = inv["totals"]
    assert t["taxable"] == 952.38
    assert t["cgst"] == 23.81 and t["sgst"] == 23.81   # intra-state (same as company UP)
    assert t["igst"] == 0.0
    assert t["grand_total"] == 1000.0
    assert inv["intra_state"] is True


def test_invoice_interstate_igst(db, product):
    seller = make_member(db, "Seller", segment="direct")
    seller.state = "Maharashtra"   # different from company (UP)
    db.commit()
    o = buy(db, seller, product, 5)   # ₹500, GST-inclusive
    inv = build_invoice(db, o)
    t = inv["totals"]
    assert t["igst"] == 23.81 and t["cgst"] == 0.0 and t["sgst"] == 0.0
    assert t["grand_total"] == 500.0
    assert inv["intra_state"] is False


def test_amount_in_words():
    assert amount_in_words(Decimal("1050.00")).startswith("One Thousand Fifty Rupees")
    assert "Paise" in amount_in_words(Decimal("873.20"))
