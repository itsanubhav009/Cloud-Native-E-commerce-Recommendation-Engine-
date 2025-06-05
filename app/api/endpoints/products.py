from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.crud import product as crud_product
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Product])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None
):
    """
    Retrieve products with optional filtering by category
    """
    return crud_product.get_products(db, skip=skip, limit=limit, category=category)

@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID
    """
    db_product = crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new product (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud_product.create_product(db=db, product=product)

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a product (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_product = crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud_product.update_product(db=db, product_id=product_id, product=product)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a product (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_product = crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    crud_product.delete_product(db=db, product_id=product_id)
    return {"detail": "Product deleted successfully"}

@router.get("/trending/", response_model=List[Product])
def get_trending_products(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get trending products based on recent user activity
    """
    return crud_product.get_trending_products(db, limit=limit)