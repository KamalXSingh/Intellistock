from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.models.products import Product
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.schemas.warehouse_stock import StockIn, StockOut,StockTransfer,ReorderLevelUpdate
from app.models.stock_movement import StockMovement

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stock",
    tags=["Warehouse Stock"]
)

@router.get("/")
def get_all_stock(
    warehouse_id:int |None=None,
    product_id:int |None=None,
    db:Session=Depends(get_db)
):
    query=db.query(WarehouseStock)
    
    if warehouse_id is not None:
        query=query.filter(
            WarehouseStock.warehouse_id == warehouse_id
        )
        
    if product_id is not None:
        query=query.filter(
            WarehouseStock.product_id==product_id
        )
        
    return query.all()

@router.post('/in')
def stock_in(
    stock_data: StockIn,
    db:Session=Depends(get_db)
):
    product=db.query(Product).filter(
        Product.id== stock_data.product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == stock_data.warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )
    
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.product_id == stock_data.product_id,
        WarehouseStock.warehouse_id == stock_data.warehouse_id
    ).with_for_update().first()
    
    try:
        if stock:
            stock.quantity +=stock_data.quantity
        else:
            stock= WarehouseStock(
                product_id=stock_data.product_id,
                warehouse_id=stock_data.warehouse_id,
                quantity=stock_data.quantity,
                reorder_level=stock_data.reorder_level
            )
            db.add(stock)
        
        #movement history
        movement = StockMovement(
            product_id=stock_data.product_id,
            warehouse_id=stock_data.warehouse_id,
            movement_type="STOCK_IN",
            quantity=stock_data.quantity
            
        )
        
        db.add(movement)
        
        db.commit()
        logger.info(
    "Stock added: product_id=%s, warehouse_id=%s, quantity=%s",
    stock.product_id,
    stock.warehouse_id,
    stock_data.quantity
)
        
        db.refresh(stock)
        
        return {
            "message": "Stock added successfully",
            "product_id": stock.product_id,
            "warehouse_id": stock.warehouse_id,
            "quantity": stock.quantity
        }
        
    except SQLAlchemyError:
        logger.exception("Failed to add stock")
        db.rollback()
        raise HTTPException(
        status_code=500,
        detail="Failed to add stock. Transaction rolled back."
    )
       
@router.post('/out')
def stock_out(
    stock_data:StockOut,
    db:Session = Depends(get_db)
):
    product = db.query(Product).filter(
        stock_data.product_id==Product.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail='Product not found'
        )
        
    warehouse = db.query(Warehouse).filter(
        Warehouse.id==stock_data.warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail='Warehouse not found'
        )
        
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.product_id == stock_data.product_id,
        WarehouseStock.warehouse_id == stock_data.warehouse_id
    ).with_for_update().first()

    if not stock:
        raise HTTPException(
            status_code=404,
            detail="No stock record found"
        )

    if stock.quantity < stock_data.quantity:
        raise HTTPException(
            status_code=409,
            detail="Insufficient stock"
        )

    try:
        stock.quantity -= stock_data.quantity

        movement = StockMovement(
            product_id=stock_data.product_id,
            warehouse_id=stock_data.warehouse_id,
            movement_type="STOCK_OUT",
            quantity=stock_data.quantity
        )
        db.add(movement)
        db.commit()
        
        logger.info(
    "Stock removed: product_id=%s, warehouse_id=%s, quantity=%s",
    stock.product_id,
    stock.warehouse_id,
    stock_data.quantity
)
        
        db.refresh(stock)

        return {
            "message": "Stock deducted successfully",
            "product_id": stock.product_id,
            "warehouse_id": stock.warehouse_id,
            "quantity": stock.quantity
        }
    except SQLAlchemyError:
        logger.exception("Failed to remove stock")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to deduct stock. Transaction rolled back."
        )
  

@router.post("/transfer")
def transfer_stock(
    transfer_data:StockTransfer,
    db:Session=Depends(get_db)
):
    if transfer_data.source_warehouse_id == transfer_data.destination_warehouse_id:
        raise HTTPException(
            status_code=400,
            detail="Source and destination warehouses must be different"
        )
        
    product = db.query(Product).filter(
        Product.id == transfer_data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    source = db.query(Warehouse).filter(
        Warehouse.id == transfer_data.source_warehouse_id
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source warehouse not found")
    
    destination = db.query(Warehouse).filter(
        Warehouse.id == transfer_data.destination_warehouse_id
    ).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destination warehouse not found")
    
    
    try:
        source_stock = db.query(WarehouseStock).filter(
            WarehouseStock.product_id == transfer_data.product_id,
            WarehouseStock.warehouse_id == transfer_data.source_warehouse_id
        ).with_for_update().first()

        if not source_stock:
            raise HTTPException(status_code=404, detail="Source stock record not found")

        if source_stock.quantity < transfer_data.quantity:
            raise HTTPException(status_code=409, detail="Insufficient stock")

        destination_stock = db.query(WarehouseStock).filter(
            WarehouseStock.product_id == transfer_data.product_id,
            WarehouseStock.warehouse_id == transfer_data.destination_warehouse_id
        ).with_for_update().first()

        source_stock.quantity -= transfer_data.quantity

        if destination_stock:
            destination_stock.quantity += transfer_data.quantity
        else:
            destination_stock = WarehouseStock(
                product_id=transfer_data.product_id,
                warehouse_id=transfer_data.destination_warehouse_id,
                quantity=transfer_data.quantity
            )
            db.add(destination_stock)

        #creating records for 
        source_movement = StockMovement(
            product_id=transfer_data.product_id,
            warehouse_id=transfer_data.source_warehouse_id,
            movement_type="TRANSFER_OUT",
            quantity=transfer_data.quantity
        )

        destination_movement = StockMovement(
            product_id=transfer_data.product_id,
            warehouse_id=transfer_data.destination_warehouse_id,
            movement_type="TRANSFER_IN",
            quantity=transfer_data.quantity
        )

        db.add(source_movement)
        db.add(destination_movement)

        db.commit()
        logger.info(
    "Stock transferred: product_id=%s, source_warehouse_id=%s, destination_warehouse_id=%s, quantity=%s",
    transfer_data.product_id,
    transfer_data.source_warehouse_id,
    transfer_data.destination_warehouse_id,
    transfer_data.quantity
)

        return {
            "message": "Stock transferred successfully",
            "product_id": transfer_data.product_id,
            "source_warehouse_id": transfer_data.source_warehouse_id,
            "destination_warehouse_id": transfer_data.destination_warehouse_id,
            "transferred_quantity": transfer_data.quantity,
            "source_remaining": source_stock.quantity,
            "destination_total": destination_stock.quantity
        }



    except SQLAlchemyError:
        logger.exception("Failed to transfer stock")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Stock transfer failed. Transaction rolled back."
        ) 
   
    
@router.patch("/{product_id}/{warehouse_id}/reorder-level")
def update_reorder_level(
    product_id: int,
    warehouse_id: int,
    data: ReorderLevelUpdate,
    db: Session = Depends(get_db)
):
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.product_id == product_id,
        WarehouseStock.warehouse_id == warehouse_id
    ).first()

    if not stock:
        raise HTTPException(
            status_code=404,
            detail="Stock record not found"
        )

    stock.reorder_level = data.reorder_level

    db.commit()
    db.refresh(stock)

    return {
        "message": "Reorder level updated successfully",
        "product_id": stock.product_id,
        "warehouse_id": stock.warehouse_id,
        "reorder_level": stock.reorder_level
    }

@router.get("/low-stock")
def get_low_stock(db: Session = Depends(get_db)):
    low_stock= db.query(WarehouseStock).options(
        joinedload(WarehouseStock.product),
        joinedload(WarehouseStock.warehouse)
    ).filter(
        WarehouseStock.quantity <= WarehouseStock.reorder_level
    ).all()
    
    logger.info(
        "Low-stock report generated: %s records found",
        len(low_stock)
    )
    
    return [
        {
            "product_id":stock.product_id,
            "product_name":stock.product.name,
            "sku":stock.product.sku,
            "warehouse_id":stock.warehouse_id,
            "warehouse_name":stock.warehouse.name,
            "warehouse_location":stock.warehouse.location,
            "quantity":stock.quantity,
            "reorder_level":stock.reorder_level,
            "reorder_quantity":stock.reorder_level - stock.quantity
            
        }
        for stock in low_stock
    ]
 
@router.get("/movements")
def get_stock_movements(
    product_id: int | None = None,
    warehouse_id: int | None = None,
    movement_type: str | None = None,
    skip:int=Query(default=0,ge=0),
    limit:int = Query(default=20,ge=0,le=100),
    db: Session = Depends(get_db)
):
    query = db.query(StockMovement).options(
        joinedload(StockMovement.product),
        joinedload(StockMovement.warehouse)
    )

    if product_id is not None:
        query = query.filter(
            StockMovement.product_id == product_id
        )

    if warehouse_id is not None:
        query = query.filter(
            StockMovement.warehouse_id == warehouse_id
        )

    if movement_type is not None:
        query = query.filter(
            StockMovement.movement_type == movement_type
        )
        
    total_results=query.count()

    movements = query.order_by(
        StockMovement.created_at.desc()
    ).offset(skip).limit(limit).all()

    
    return {
        "total_recors":total_results,
        "skip":skip,
        "limit":limit,
        "data":[
        {
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": movement.product.name,
            "sku": movement.product.sku,
            "warehouse_id": movement.warehouse_id,
            "warehouse_name": movement.warehouse.name,
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "created_at": movement.created_at
        }
        for movement in movements
        ]
    }
    
@router.get("/summary")
def get_stock_summary(db:Session =Depends(get_db)):
    
    total_products=db.query(
        func.count(func.distinct(WarehouseStock.product_id))
    ).scalar()
    
    total_units=db.query(
        func.sum(WarehouseStock.quantity)
    ).scalar()
    
    low_stock_count = db.query(
        func.count(WarehouseStock.id)
    ).filter(
        WarehouseStock.quantity <= WarehouseStock.reorder_level
    ).scalar()
    
    out_of_stock_count=db.query(
        func.count(WarehouseStock.id)
    ).filter(
        WarehouseStock.quantity==0
    ).scalar()
    
    active_warehouses=db.query(
        func.count(Warehouse.id)
    ).filter(
        Warehouse.is_active == True
    ).scalar()
    logger.info("Inventory summary generated successfully")
    return{
        "total_products":total_products,
        "total_units": total_units or 0,
        "low_stock_count":low_stock_count,
        "out_of_stock_count":out_of_stock_count,
        "active_warehouses":active_warehouses   
    }