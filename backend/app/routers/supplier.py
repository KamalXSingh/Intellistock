from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database.connection import get_db
from app.models.suppliers import Supplier
from app.schemas.suppliers import SupplierCreate,SupplierResponse,SupplierUpdate
from app.models.products import Product
from app.schemas.suppliers import MessageResponse

router= APIRouter(
    prefix='/suppliers',
    tags=["Suppliers"]
)

@router.post("/")
def create_supplier(
    supplier:SupplierCreate,
    db:Session= Depends(get_db)
):
    new_supplier = Supplier(**supplier.model_dump())
    
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    
    return {
        "success": True,
        "message": "Supplier created successfully",
        "data": new_supplier
}

@router.get("/")
def get_suppliers(db:Session =Depends(get_db)):
    suppliers=db.query(Supplier).options(
        joinedload(Supplier.products)).all()
    return {
        "success": True,
        "message": "Suppliers retrieved successfully",
        "data": suppliers
}

@router.get("/{supplier_id}")
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).options(joinedload(Supplier.products)).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return {
        "success": True,
        "message": "Supplier retrieved successfully",
        "data": supplier
}

@router.patch("/{supplier_id}")
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    update_data = supplier_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)

    return {
        "success": True,
        "message": "Supplier updated successfully",
        "data": supplier
}

@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    # Check whether any products use this supplier
    linked_products = db.query(Product).filter(
        Product.supplier_id == supplier_id
    ).first()

    if linked_products:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete supplier because products are linked to it"
        )

    db.delete(supplier)
    db.commit()

    return {
        "success": True,
        "message": "Supplier deleted successfully",
        "data": None
}