from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.models.category import Category
from app.models.products import Product
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    MessageResponse
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)
@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    new_category = Category(**category.model_dump())

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    return new_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(category, key, value)

    try:
        db.commit()
        db.refresh(category)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists"
        )

    return category

@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check whether products are assigned to this category
    products_exist = db.query(Product).filter(
        Product.category_id == category_id
    ).first()

    if products_exist:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category because products are assigned to it"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}