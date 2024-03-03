# PDM
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from gridfs import GridFS
from openai import OpenAI
from pymongo import errors

import recruit_tracker_api.utils as utils
from recruit_tracker_api.constants import MONGO_URL as url
from recruit_tracker_api.constants import OPENAI_API_KEY
from recruit_tracker_api.mongo import init_mongo

student_router = APIRouter()

client = OpenAI(api_key=OPENAI_API_KEY)


@student_router.post("/student/query")
async def read(request: Request):
    try:
        request_json = await request.json()
        content = request_json["content"]
        filter_conditions = request_json.get("filter", {})

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        result = user_collection.find(filter_conditions)
        result_list = list(result)

        for user in result_list:
            resume_hash = user.get("resume_hash")
            pdf = db.fs.pdfs.find_one({"metadata.hash": resume_hash})
            user["resume"] = pdf

        client.close()

        return JSONResponse(content={"users": result_list}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@student_router.post("/student")
async def create(request: Request):
    try:
        json = await request.json()
        user = json["user"]

        assert user.get("email")

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        # hash password
        hash_pw = utils.hash_password(user.get("password"))
        user["password"] = hash_pw

        pdf = user.get("resume")

        if pdf:
            file_hash = utils.store_pdf(db, pdf)  # store pdf in db
            user["resume_hash"] = file_hash

        user_collection.insert_one({"_id": user.get("email"), **user})

        client.close()
        return JSONResponse(content={"creation": str("success")}, status_code=200)

    except errors.DuplicateKeyError:
        return JSONResponse(
            content={"error": "Account with that email already exists."},
            status_code=409,
        )

    # except Exception as e:
    #     print(e)
    #     return JSONResponse(content={"error": str(e)}, status_code=500)


@student_router.post("/student/update")
async def update(request: Request):
    try:
        json = await request.json()
        user = json["user"]
        assert user.get("email")

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        user_collection.update_one({"_id": user.get("email")}, {"$set": {**user}})
        client.close()

        return JSONResponse(content={"update": "success"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@student_router.post("/student/delete")
async def delete(request: Request):
    try:
        json = await request.json()
        user = json["user"]
        assert user.get("email")

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        user_collection.delete_one({"_id": user.get("email")})
        return JSONResponse(content={"update": "success"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=200)


@student_router.post("/api/login")
async def login(request: Request):
    try:
        json_data = await request.json()
        user = json_data.get("user")
        assert (
            user and user.get("email") and user.get("password")
        ), "Email and password are required."

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        user_email = user.get("email")

        result = user_collection.find_one({"email": user_email})

        if not result:
            raise HTTPException(status_code=401, detail="Email not found.")

        if not utils.verify_password(user.get("password"), result.get("password")):
            raise HTTPException(
                status_code=401, detail="Password does not match email."
            )

        # success
        token = utils.create_jwt_token(user)

        return JSONResponse(
            content={"login": "Login successful!", "token": token}, status_code=200
        )

    except HTTPException as he:
        return JSONResponse(
            content={"login": str(he.detail)}, status_code=he.status_code
        )

    except AssertionError as ae:
        return JSONResponse(content={"error": str(ae)}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@student_router.post("/api/testgpt")
async def test_gpt(request: Request):
    request_json = await request.json()
    user_input = request_json["data"]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a programming devops expert",
            },
            {
                "role": "user",
                "content": user_input,  # Use the extracted user input
            },
        ],
    )

    text = completion.choices[0].message  # Extract the text from the completion
    return {"text": text}
