# PDM
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

hr_router = APIRouter()


@hr_router.get("/")
async def root():
    return {"message": "FAST!"}
