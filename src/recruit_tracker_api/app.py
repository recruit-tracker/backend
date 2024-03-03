from fastapi import FastAPI

from recruit_tracker_api.routes import hr_router, student_router

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hr_router)
app.include_router(student_router)
