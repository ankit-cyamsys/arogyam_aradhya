from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Category, Product
from app.schemas import CategoryOut, ProductOut

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.execute(select(Category).order_by(Category.name)).scalars().all()


@router.get("/products", response_model=list[ProductOut])
def list_products(
    category: str | None = Query(default=None, description="category slug"),
    offer: bool | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Product).where(Product.is_active.is_(True))
    if category:
        stmt = stmt.join(Category).where(Category.slug == category)
    if offer is not None:
        stmt = stmt.where(Product.is_offer.is_(offer))
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    return db.execute(stmt.order_by(Product.name)).scalars().all()


@router.get("/products/{slug}", response_model=ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.execute(select(Product).where(Product.slug == slug)).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
