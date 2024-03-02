from fastapi import FastAPI

from recruit_tracker_api.routes import router

app = FastAPI()
app.include_router(router)
