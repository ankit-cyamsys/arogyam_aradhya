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
}

# Official catalog (from the business-confirmed MRP/DP/SP sheet). DP is the base
# price and is GST-inclusive; MRP is retail. No offer packs — DP is the only
# price point members transact on.
# (name, category_slug, sp, mrp, dp, image)
PRODUCTS = [
    ("Anti Addiction Drop 30ml", "wellness", 2, 499, 370, "anti-addiction-drop.jpg"),
    ("Tulsi Amrit Drop 30ml", "immunity", 0.75, 249, 149, "tulsi-amrit-drop.jpg"),
    ("Kanth Shuddhi Cough Syrup 200ml", "wellness", 1, 249, 149, "kanth-shuddhi-cough-syrup.jpg"),
    ("Slim-Fit Amrit Syrup 500ml", "wellness", 5, 999, 700, "slimfit-amrit-syrup.jpg"),
    ("Slim-Fit Amrit Capsule 30", "wellness", 5, 999, 649, "slimfit-amrit-capsule.jpg"),
    ("Ortho Amrit Ras 200ml", "wellness", 1.5, 299, 199, "ortho-amrit-ras.jpg"),
    ("Ortho Amrit Capsule 30", "wellness", 1.5, 299, 199, "ortho-amrit-capsule.jpg"),
    ("Aradhya Super Mixberry Amrit Juice 500ml", "wellness", 10, 1699, 1299, "mixberry-juice.jpg"),
    ("Amla Tulsi Ginger Curcumin Gold Juice 800ml", "immunity", 2, 499, 280, "amla-tulsi-ginger.jpg"),
    ("Pure Ghrit Kumari (Aloevera) Juice 800ml", "digestive", 2.5, 899, 425, "ghrit-kumari-juice.jpg"),
    ("Energy & Stamina 3X Power Wellness Kit", "wellness", 6, 1499, 999, "energy-stamina-kit.jpg"),
    ("Pure Skin Neem Aloevera Face Wash 200ml", "skin-care", 0.75, 299, 175, "neem-aloevera-facewash.jpg"),
    ("De-Tan Coffee Face Wash 200ml", "skin-care", 0.75, 299, 175, "coffee-facewash.jpg"),
    ("Pollution Defense Charcoal Face Wash 200ml", "skin-care", 0.75, 299, 175, "charcoal-facewash.jpg"),
    ("Amla Shikakai Shampoo 200ml", "personal-care", 0.75, 299, 175, "amla-shikakai-shampoo.jpg"),
    ("Tasty Pachak Hing Goli 50gm", "digestive", 0.1, 99, 65, "tasty-pachak-hing-goli.jpg"),
    ("Chatpati Hing Dana 50gm", "digestive", 0.2, 119, 85, "chatpati-hing-dana.jpg"),
    ("Hing Goli Bada Dana 50gm", "digestive", 0.2, 92, 75, "hing-goli-bada-dana.jpg"),
    ("Maha-Ortho Sanjavani Pain Guard Rolon 50ml", "wellness", 1.5, 349, 249, "pain-guard-rolon.jpg"),
    ("Coughnip Syrup 100ml", "wellness", 0.25, 149, 75, "coughnip-syrup.jpg"),
    ("Kass Care Syrup 100ml", "wellness", 0.25, 149, 75, "kass-care-syrup.jpg"),
    ("Giloy Papaya Wheatgrass 500ml", "immunity", 2, 525, 299, "giloy-papaya-wheatgrass.jpg"),
    ("Livozyme 200ml", "digestive", 1, 249, 149, "livozyme.jpg"),
    ("Livozyme-DS Syrup 200ml", "digestive", 1, 249, 149, "logo.jpeg"),
    ("Seetone 200ml", "wellness", 1, 249, 149, "seetone.jpg"),
    ("Neem Soap 75gm", "personal-care", 0.1, 90, 45, "neem-soap.jpg"),
    ("Aloevera Shampoo 500ml", "personal-care", 1, 349, 249, "aloevera-shampoo.jpg"),
    ("Gas Go 100gm", "digestive", 1, 249, 149, "gas-go.jpg"),
    ("Jyoti Rakshak Eye Drops 10ml", "wellness", 0.2, 125, 75, "eye-drops.jpg"),
    ("Sanitary Pads", "personal-care", 0.5, 249, 149, "sanitary-pad.jpg"),
    ("Smart Bag", "home-care", 2, 999, 700, "logo.jpeg"),
    ("Energy & Stamina 3X Power Wellness Oil", "wellness", 1, 399, 299, "energy-stamina-oil.jpg"),
    ("Energy & Stamina 3X Power Wellness 30 Pak", "wellness", 3, 999, 499, "energy-stamina-30pak.jpg"),
    ("Energy & Stamina 3X Power Wellness Juice 500ml", "wellness", 3, 999, 549, "logo.jpeg"),
    ("Aradhya Platelet GPW Syrup 200ml", "immunity", 1, 249, 149, "logo.jpeg"),
    ("Aradhya Livo+ 100ml", "digestive", 0.5, 149, 75, "logo.jpeg"),
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
            for name, cslug, sp, mrp, dp, img in PRODUCTS:
                db.add(Product(
                    name=name,
                    slug=slugify(name),
                    description=DESCRIPTION,
                    category_id=cat_by_slug[cslug].id,
                    mrp=Decimal(str(max(mrp, dp))),  # guard against DP > MRP in source data
                    price=Decimal(str(dp)),          # DP = distributor/discount price (base), GST-inclusive
                    cost_price=Decimal("0"),
                    sp=Decimal(str(sp)),
                    stock=100,
                    image=f"/static/products/{img}",
                    is_active=True, is_offer=False,
                ))
            db.commit()
            print(f"Seeded {len(PRODUCTS)} products.")

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
