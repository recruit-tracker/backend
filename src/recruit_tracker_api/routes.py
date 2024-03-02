# PDM
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "FAST!"}
