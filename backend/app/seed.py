"""Create tables and seed demo data.

Run:  python -m app.seed        (from the backend/ folder, venv active)
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import AdminUser, Category, Member, Product
from app.services import settings_service as cfg
from app.utils.text import slugify

# category slug -> display name
CATEGORIES = {
    "immunity": "Immunity Boosters",
    "digestive": "Digestive Health",
    "skin-care": "Skin Care",
    "wellness": "General Wellness",
    "personal-care": "Personal Care",
    "home-care": "Home Care",
    "offers": "Offer Packages",
}

# Official catalog (PRODUCT LIST AROGYAM ARADHYA). DP is the base price; MRP is retail.
# (name, category_slug, sp, mrp, dp, image, is_offer)
PRODUCTS = [
    ("Anti Addiction Drop 30ml", "wellness", 2, 499, 370, "logo.jpeg", False),
    ("Tulsi Drop 30ml", "immunity", 0.75, 249, 149, "logo.jpeg", False),
    ("Cough Syrup 200ml", "wellness", 1, 249, 149, "cough-syrup.jpg", False),
    ("Weight Loss Syrup 500ml", "wellness", 5, 999, 700, "weightloss-syrup.jpg", False),
    ("Weight Loss Capsule 30", "wellness", 5, 999, 649, "weightloss-cap.jpg", False),
    ("Ortho Syrup 200ml", "wellness", 1.5, 299, 199, "ortho-syrup.jpg", False),
    ("Ortho Capsule 30", "wellness", 1.5, 299, 199, "ortho-cap.jpg", False),
    ("Mixberry Juice 500ml", "wellness", 10, 1699, 1299, "energy-stamina.jpg", True),
    ("Amla Tulsi Ginger Curcumin 800ml", "immunity", 2, 499, 280, "logo.jpeg", False),
    ("Aloevera with Fiber 800ml", "digestive", 2.5, 899, 425, "neem-aloevera.jpg", False),
    ("Energy & Stamina 3X Power Wellness Kit", "wellness", 6, 1499, 1499, "energy-stamina.jpg", True),
    ("Neem Aloevera Face Wash", "skin-care", 0.75, 299, 175, "neem-facewash.jpg", False),
    ("Coffee Face Wash", "skin-care", 0.75, 299, 175, "coffee-facewash.jpg", False),
    ("Charcoal Face Wash 200ml", "skin-care", 0.75, 299, 175, "coffee-facewash.jpg", False),
    ("Amla Shikakai Shampoo 200ml", "personal-care", 0.75, 299, 175, "aloevera-shampoo.jpg", False),
    ("Hinggoli", "digestive", 0.1, 99, 65, "hing-goli.jpg", False),
    ("Hing Goli Dana", "digestive", 0.2, 119, 85, "hingoli.jpg", False),
    ("Pain Guard Roll-On", "wellness", 1, 299, 199, "pain-rolon.jpg", False),
    ("Cough Syrup 100ml", "wellness", 0.25, 149, 149, "cough-syrup-100.jpg", False),
    ("Giloy Papaya Wheatgrass", "immunity", 2, 525, 299, "giloy-papaya.jpg", False),
    ("Livzyme", "digestive", 1, 249, 149, "livzyme.jpg", False),
    ("Seetone", "wellness", 1, 249, 149, "seetone.jpg", False),
    ("Neem Soap", "personal-care", 0.1, 90, 45, "neem-soap.jpg", False),
    ("Herbal Shampoo", "personal-care", 1, 349, 249, "aloevera-shampoo.jpg", False),
    ("Gas Go", "digestive", 1, 249, 149, "gas-go.jpg", False),
    ("Eye Drop", "wellness", 0.25, 125, 75, "logo.jpeg", False),
    ("Sanitary Pads", "personal-care", 0.5, 249, 149, "sanitary-pad.jpg", False),
    ("Smart Bag", "home-care", 2.5, 999, 700, "logo.jpeg", False),
]

# Business/offer packages (SP values are estimates — confirm & adjust in admin).
# (name, sp, price, image)
OFFER_PACKAGES = [
    ("Starter Offer Pack", 40, 5000, "offer-5000.jpg"),
    ("Silver Offer Pack", 100, 12500, "offer-12500.jpg"),
    ("Gold Offer Pack", 200, 25000, "offer-25000.jpg"),
    ("Platinum Offer Pack", 400, 50000, "offer-50000.jpg"),
]

DESCRIPTION = (
    "Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, "
    "no side effects, made with trusted quality ingredients."
)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cfg.seed_defaults(db)
        cfg.set_value(db, "company_name", settings.COMPANY_NAME)

        # Admin
        if not db.execute(select(AdminUser)).scalars().first():
            db.add(AdminUser(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                name="Administrator",
            ))
            db.commit()
            print(f"Admin created: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")

        # Categories
        cat_by_slug: dict[str, Category] = {}
        for slug, name in CATEGORIES.items():
            cat = db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()
            if cat is None:
                cat = Category(slug=slug, name=name)
                db.add(cat)
            cat_by_slug[slug] = cat
        db.commit()

        # Products
        if not db.execute(select(Product)).scalars().first():
            for name, cslug, sp, mrp, dp, img, offer in PRODUCTS:
                db.add(Product(
                    name=name,
                    slug=slugify(name),
                    description=DESCRIPTION,
                    category_id=cat_by_slug[cslug].id,
                    mrp=Decimal(str(max(mrp, dp))),  # guard against DP > MRP in source data
                    price=Decimal(str(dp)),          # DP = distributor/discount price (base)
                    cost_price=Decimal("0"),
                    sp=Decimal(str(sp)),
                    stock=100,
                    image=f"/static/products/{img}",
                    is_active=True, is_offer=offer,
                ))
            for name, sp, price, img in OFFER_PACKAGES:
                db.add(Product(
                    name=name,
                    slug=slugify(name),
                    description="Business offer package — includes products worth the pack value.",
                    category_id=cat_by_slug["offers"].id,
                    mrp=Decimal(str(price)), price=Decimal(str(price)),
                    cost_price=Decimal("0"), sp=Decimal(str(sp)), stock=1000,
                    image=f"/static/products/{img}",
                    is_active=True, is_offer=True,
                ))
            db.commit()
            print(f"Seeded {len(PRODUCTS)} products + {len(OFFER_PACKAGES)} offer packs.")

        # Founder / root of the binary tree — the top sponsor for all signups.
        if not db.execute(select(Member)).scalars().first():
            root = Member(
                member_id=f"{settings.MEMBER_ID_PREFIX}10000001",
                segment="mlm",
                name="Arogyam Aradhya",
                phone="9000000001",
                password_hash=hash_password("Founder@2026"),
                is_active=True,
            )
            db.add(root)
            db.commit()
            print(f"Founder root: {root.member_id} / Founder@2026")

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
