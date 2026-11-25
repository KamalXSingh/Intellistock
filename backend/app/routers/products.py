
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.models.products import Product
from app.schemas.product import ProductCreate, ProductUpdate,ProductResponse,MessageResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)




# GET all products
@router.get("/",response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.category),
                                         joinedload(Product.supplier)).all()
    return products


# GET product by ID
@router.get("/{product_id}",response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).options(joinedload(Product.category),
                                        joinedload(Product.supplier)
                                        ).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# CREATE product
@router.post("/",response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(**product.model_dump())

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
    except IntegrityError as e:
        db.rollback()
        print("Constraint name:", e.orig.diag.constraint_name)

        error_message = str(e.orig)

        if "products_category_id_fkey" in error_message:
            detail = "Invalid category_id"

        elif "products_supplier_id_fkey" in error_message:
            detail = "Invalid supplier_id"

        elif "products_sku_key" in error_message:
            detail = "SKU already exists"

        else:
            detail = "Database constraint violation"

        raise HTTPException(
            status_code=409,
            detail=detail
        )

    return new_product


# PARTIALLY UPDATE product
@router.patch("/{product_id}",response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    updated_data = product.model_dump(exclude_unset=True)

    try:
        for key, value in updated_data.items():
            setattr(existing_product, key, value)

        db.commit()
        db.refresh(existing_product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database constraint violation. Check whether the SKU already exists."
        )

    return existing_product


# COMPLETELY REPLACE product
@router.put("/{product_id}",response_model=ProductResponse)
def replace_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    updated_data = product.model_dump()

    try:
        for key, value in updated_data.items():
            setattr(existing_product, key, value)

        db.commit()
        db.refresh(existing_product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database constraint violation. Check whether the SKU already exists."
        )

    return existing_product


# DELETE product
@router.delete("/{product_id}",response_model=MessageResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:
        db.delete(existing_product)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Cannot delete product because it has associated records"
    )

    return {"message": "Product deleted successfully"}


@router.get("/{product_id}/supplier")
def get_product_supplier(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not product.supplier:
        return {"message": "No supplier assigned"}

    return {
        "product_name": product.name,
        "supplier_id": product.supplier.id,
        "supplier_name": product.supplier.name
    }
    
    
    
    
    