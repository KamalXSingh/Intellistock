from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)


class CategoryUpdate(BaseModel):
    name: str = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str