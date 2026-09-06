from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
import app.models  # noqa: F401  (register all models)
from app.core.security import hash_password
from app.models import Member, Product, Category, Order, OrderItem
from app.services import settings_service as cfg
from app.services import tree
from app.services.ids import generate_member_id, generate_order_no
from app.services.mlm_engine import process_order


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, future=True)
    s = Session()
    cfg.seed_defaults(s)
    try:
        yield s
    finally:
        s.close()


@pytest.fixture()
def product(db):
    cat = Category(name="Wellness", slug="wellness")
    db.add(cat)
    db.flush()
    # 1 SP unit priced at ₹100 DP so SP math is easy to reason about
    p = Product(name="Test SP Pack", slug="test-sp", category_id=cat.id,
                mrp=Decimal("100"), price=Decimal("100"), cost_price=Decimal("0"),
                sp=Decimal("1"), stock=100000, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def make_member(db, name, segment="mlm", sponsor=None, position="L", active=False):
    parent_id = None
    leg = None
    sponsor_id = None
    if sponsor is not None:
        sponsor_id = sponsor.id
        parent, leg = tree.find_placement(db, sponsor, position)
        parent_id = parent.id
    m = Member(
        member_id=generate_member_id(db), segment=segment, name=name,
        phone=generate_member_id(db), password_hash=hash_password("x"),
        sponsor_id=sponsor_id, parent_id=parent_id, position=leg, is_active=active,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def buy(db, member, product, sp_amount):
    """Place a paid order giving `sp_amount` SP (product is 1 SP each).

    Mirrors the order route: subtotal is the taxable base, total adds GST when
    prices are GST-exclusive.
    """
    qty = int(sp_amount)
    subtotal = Decimal(str(product.price)) * qty
    gst_rate = Decimal(str(cfg.get(db, "gst_rate", 18)))
    inclusive = bool(cfg.get(db, "price_gst_inclusive", False))
    total = subtotal if inclusive else (subtotal * (Decimal("1") + gst_rate / Decimal("100"))).quantize(Decimal("0.01"))
    o = Order(order_no=generate_order_no(db), member_id=member.id, status="paid",
              payment_status="paid", subtotal=subtotal,
              total=total, total_sp=Decimal(str(product.sp)) * qty)
    o.items.append(OrderItem(product_id=product.id, name=product.name,
                             price=product.price, sp=product.sp, quantity=qty))
    db.add(o)
    db.commit()
    db.refresh(o)
    process_order(db, o)
    db.refresh(member)
    return o
