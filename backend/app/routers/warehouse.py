from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.models.warehouse import Warehouse
from app.models.products import Product
from app.models.warehouse_stock import WarehouseStock
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    MessageResponse
)

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)

@router.post('/',status_code=201)
def create_warehouse(
    warehouse:WarehouseCreate,
    db:Session = Depends(get_db)
):
    new_warehouse= Warehouse(**warehouse.model_dump())
    
    db.add(new_warehouse)
    
    try:
        db.commit()
        db.refresh(new_warehouse)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Warehouse with the name already exists"
        )
        
    return {
        "success": True,
        "message": "Warehouse created successfully",
        "data": new_warehouse
}

@router.get("/")
def get_warehouses(db:Session=Depends(get_db)):
    warehouses= db.query(Warehouse).all()
    
    return {
        "success": True,
        "message": "Warehouses retrieved successfully",
        "data": warehouses
}

@router.get("/{warehouse_id}")
def get_warehouse(warehouse_id:int,db:Session = Depends(get_db)):
    warehouse=db.query(Warehouse).filter(
        Warehouse.id==warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse Not Found"
        )
        
    return {
        "success": True,
        "message": "Warehouse retrieved successfully",
        "data": warehouse
}

@router.patch("/{warehouse_id}")
def update_warehouse(
    warehouse_id:int,
    warehouse_data:WarehouseUpdate,
    db:Session = Depends(get_db)
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id
    ).first()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )
        
    update_data = warehouse_data.model_dump(exclude_unset=True)
    
    for key,value in update_data.items():
        setattr(warehouse,key,value)
    try:
        db.commit()
        db.refresh(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Warehouse with this name already exists"
        )

    return {
        "success": True,
        "message": "Warehouse updated successfully",
        "data": warehouse
}


@router.delete("/{warehouse_id}",status_code=202)
def delete_warehouse(
    warehouse_id:int,
    db:Session= Depends(get_db)
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.id==warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )
    
    existing_stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == warehouse_id
    ).first()
    
    if existing_stock:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete warehouse because it has stock records"
        )

    db.delete(warehouse)
    db.commit()

    return {
        "success": True,
        "message": "Warehouse deleted successfully",
        "data": None
}