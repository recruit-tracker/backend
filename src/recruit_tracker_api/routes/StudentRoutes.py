# PDM
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

student_router = APIRouter()


@student_router.get("/")
async def root():
    return {"message": "FAST!"}
