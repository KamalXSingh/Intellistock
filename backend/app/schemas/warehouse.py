from pydantic import BaseModel, Field


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=200)


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    location: str | None = Field(default=None, min_length=2, max_length=200)
    is_active: bool | None = None


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: str
    is_active: bool

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
