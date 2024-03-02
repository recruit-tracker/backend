# PDM
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from openai import OpenAI

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
        filter_conditions = request_json.get(
            "filter", {}
        )  # Default to an empty filter if not provided

        client = init_mongo(url)
        db = client["recruit_tracker"]
        user_collection = db["users"]

        # Apply the filter conditions to the query
        result = user_collection.find(filter_conditions)

        # Convert the result to a list if needed
        result_list = list(result)

        # Close the MongoDB connection
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

        user_collection.insert_one({"_id": user.get("email"), **user})
        
        return JSONResponse(content={"creation": str("success")}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@student_router.get("/student/update")
async def update():
    ...


@student_router.get("/student/delete")
async def delete():
    ...


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
