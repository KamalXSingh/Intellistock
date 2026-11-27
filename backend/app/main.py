from app.routers import products
from app.routers import supplier
from app.routers import categories
from app.routers import warehouse
from app.routers import warehouse_stock
from app.routers import auth
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError


from app.exceptions.handlers import http_exception_handler,validation_exception_handler,generic_exception_handler
from app.core.logging_config import setup_logging





setup_logging()



app = FastAPI(
    title="IntelliStock API",
    description="Intelligent Inventory Management System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to IntelliStock API",
        "status": "running"
    }

app.add_exception_handler(
    HTTPException,
    http_exception_handler
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)
app.add_exception_handler(
    Exception,
    generic_exception_handler
)

app.include_router(products.router)
app.include_router(supplier.router)
app.include_router(categories.router)
app.include_router(warehouse.router)
app.include_router(warehouse_stock.router)
app.include_router(auth.router)







