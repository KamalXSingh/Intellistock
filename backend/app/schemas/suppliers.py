from pydantic import BaseModel,Field

class SupplierCreate(BaseModel):
    name:str = Field(min_length=2,max_length=100)
    
class SupplierUpdate(BaseModel):
    name:str= Field(default=None,min_length=2,max_length=100)
    
class SupplierResponse(BaseModel):
    id:int
    name:str
    
    model_config={
        "from_attributes":True
    }
    
class MessageResponse(BaseModel):
    message:str