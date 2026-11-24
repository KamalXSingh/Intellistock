from pydantic import BaseModel,Field

class SupplierInfo(BaseModel):
    id:int
    name:str
    
    model_config={"from_attributes":True}

class CategoryInfo(BaseModel):
    id:int
    name:str
    
    model_config={"from_attributes":True}

class ProductCreate(BaseModel):
    name:str =Field(min_length=3, max_length=100)
    category_id: int = Field(default=None, gt=0)
    supplier_id:int | None = None
    price: float =Field(gt=0)
    sku:str =Field(min_length=3, max_length=30)
    description:str | None= Field(default=None,max_length=300)
    is_active: bool =False
    
class ProductUpdate(BaseModel):
    name: str = Field(default=None, min_length=3, max_length=100)
    category_id: int = Field(default=None, gt=0)
    supplier_id:int|None = None
    price: float = Field(default=None, gt=0)
    sku: str = Field(default=None, min_length=3, max_length=30)
    description: str | None = Field(default=None, max_length=300)
    is_active: bool = Field(default=None)

class ProductResponse(BaseModel):
    id:int
    name:str
    supplier_id:int |None
    supplier: SupplierInfo | None
    category_id:int
    category:CategoryInfo
    price:float
    sku:str
    description:str | None
    is_active:bool
    
    model_config={"from_attributes":True}
    
class MessageResponse(BaseModel):
    message:str