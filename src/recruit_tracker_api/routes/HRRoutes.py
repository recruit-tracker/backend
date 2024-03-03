# PDM
import csv
import json

import jwt
import pymongo
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

import recruit_tracker_api.utils as utils
from recruit_tracker_api.constants import MONGO_URL as url
from recruit_tracker_api.mongo import init_mongo

hr_router = APIRouter()


@hr_router.get("/")
async def root():
    return {"message": "FAST!"}


from fastapi.responses import JSONResponse


@hr_router.post("/admin/import")
async def import_csv(request: Request):
    try:
        json_data = await request.json()
        path = json_data.get("path")
        assert "path" in path

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        json_csv = utils.csv_to_json(path["path"])

        user_collection.insert_many(json_csv)

        client.close()

        return JSONResponse(content={"Import": "Import Successful!"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# print(utils.csv_to_json("../test.csv"))
