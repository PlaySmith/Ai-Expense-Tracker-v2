from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            {"detail": "Endpoint not found. Check /docs"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        return JSONResponse(
            {"detail": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

