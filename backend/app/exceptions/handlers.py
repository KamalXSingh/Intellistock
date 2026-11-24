from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(
    request:Request,
    exc:HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "sucess":False,
            "message":exc.detail
        }
    )
    
async def validation_exception_handler(
    request:Request,
    exc:RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": exc.errors()
        }
    )
    
async def generic_exception_handler(
    request:Request,
    exc:Exception
):
    logger.exception(
        "Unexpected error occurred while processing %s %s",
        request.method,
        request.url
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success":False,
            "message":"Internal Server Error"
        }
    )