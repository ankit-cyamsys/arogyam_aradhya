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
from app.services import tree
from app.services.ids import generate_member_id
from app.utils.text import slugify

# category slug -> display name
CATEGORIES = {
    "immunity": "Immunity Boosters",
    "digestive": "Digestive Health",
    "skin-care": "Skin Care",
    "wellness": "General Wellness",
    "home-care": "Home Care",
    "personal-care": "Personal Care",
}

# Real catalog from the company price list.
# (name, category_slug, cost_price, dp, sp, image, is_offer)  — DP is the base price, 1 SP = ₹10
PRODUCTS = [
    ("Honisys 100ML", "wellness", 9, 75, 0.2, "p02.jpeg", False),
    ("Aarogyam Dant Muskan 100gm", "personal-care", 29, 99, 0.3, "p03.jpeg", False),
    ("Aarogyam Pet Shanti Heeng Goli", "digestive", 17, 85, 0.2, "p04.jpeg", True),
    ("Aloevera", "wellness", 70, 425, 2, "p05.jpeg", False),
    ("Aloevera Hand Wash 250ML", "home-care", 40, 75, 0.1, "p06.jpeg", False),
    ("Amla Ras 1000ML", "immunity", 70, 280, 1, "p07.jpeg", False),
    ("Amla Shikakai Shampoo 200ML", "personal-care", 65, 210, 0.5, "p08.jpeg", False),
    ("Amrit Mix Berry Juice 1000ML", "wellness", 150, 2100, 15, "p09.jpeg", True),
    ("Anti Addiction", "wellness", 40, 370, 2, "p10.jpeg", False),
    ("Arjuna", "wellness", 50, 255, 1.5, "p11.jpeg", False),
    ("Charcoal Facewash 200ML", "skin-care", 65, 199, 0.5, "p12.jpeg", False),
    ("Diabetic 1000ML", "wellness", 150, 1499, 10, "p13.jpeg", False),
    ("Dish Wash 500ML", "home-care", 50, 78, 0.1, "p14.jpeg", False),
    ("Giloy Papaya Wheatgrass", "immunity", 50, 299, 1.5, "p15.jpeg", False),
    ("Heart Care 1000ML", "wellness", 150, 1920, 13, "p16.jpeg", False),
    ("Livozyme 200ML", "digestive", 20, 149, 0.75, "p01.jpeg", False),
    ("Moringa 500ML", "wellness", 85, 749, 5, "p17.jpeg", False),
    ("Nari Sanjeevani Shakti 500ML", "wellness", 100, 745, 5, "p18.jpeg", True),
    ("Ortho Care 500ML", "wellness", 100, 700, 5, "p19.jpeg", False),
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
            for name, cslug, cost, dp, sp, img, offer in PRODUCTS:
                db.add(Product(
                    name=name,
                    slug=slugify(name),
                    description=DESCRIPTION,
                    category_id=cat_by_slug[cslug].id,
                    mrp=Decimal(str(dp)),          # no separate MRP supplied; DP is the base
                    price=Decimal(str(dp)),        # DP = distributor/discount price
                    cost_price=Decimal(str(cost)),
                    sp=Decimal(str(sp)),
                    stock=100,
                    image=f"/static/products/{img}",
                    is_active=True, is_offer=offer,
                ))
            db.commit()
            print(f"Seeded {len(PRODUCTS)} products.")

        # Demo network (root + a few placed members) for the genealogy tree
        if not db.execute(select(Member)).scalars().first():
            root = Member(
                member_id=generate_member_id(db),
                name="Demo Root",
                phone="9000000001",
                email="demo@arogyamaradhya.com",
                password_hash=hash_password("demo123"),
                is_active=True,
            )
            db.add(root)
            db.commit()
            db.refresh(root)

            names = ["Ambika Yadav", "Ganesh Kumar", "Saroj Devi", "Ramesh Yadav",
                     "Sunita Sharma", "Vijay Gupta", "Anita Devi"]
            for i, nm in enumerate(names):
                parent, leg = tree.find_placement(db, root, "L" if i % 2 == 0 else "R")
                m = Member(
                    member_id=generate_member_id(db),
                    name=nm,
                    phone=f"90000000{10 + i}",
                    password_hash=hash_password("demo123"),
                    sponsor_id=root.id,
                    parent_id=parent.id,
                    position=leg,
                    is_active=(i % 2 == 0),
                )
                db.add(m)
                db.commit()
            print(f"Demo MLM root member: {root.member_id} / demo123")

            seller = Member(
                member_id=generate_member_id(db),
                segment="direct",
                name="Demo Seller",
                phone="9000000099",
                email="seller@arogyamaradhya.com",
                password_hash=hash_password("demo123"),
                is_active=True,
            )
            db.add(seller)
            db.commit()
            db.refresh(seller)
            print(f"Demo Direct seller: {seller.member_id} / demo123")

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
