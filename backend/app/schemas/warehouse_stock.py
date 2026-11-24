from pydantic import BaseModel,Field

class StockIn(BaseModel):
    product_id:int =Field(gt=0)
    warehouse_id:int = Field(gt=0)
    quantity:int =Field(gt=0)
    reorder_level:int=Field(default=10,ge=0)
    
class StockOut(BaseModel):
    product_id:int =Field(gt=0)
    warehouse_id:int=Field(gt=0)
    quantity:int =Field(gt=0)
    
class StockTransfer(BaseModel):
    product_id:int = Field(gt=0)
    source_warehouse_id:int =Field(gt=0)
    destination_warehouse_id:int =Field(gt=0)
    quantity:int = Field(gt=0)
    
class ReorderLevelUpdate(BaseModel):
    reorder_level: int = Field(ge=0)