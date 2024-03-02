from fastapi import FastAPI

from recruit_tracker_api.routes import hr_router, student_router

app = FastAPI()
app.include_router(hr_router)
app.include_router(student_router)
