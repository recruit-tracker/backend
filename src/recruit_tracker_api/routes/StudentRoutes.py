# PDM
import requests
from fastapi import APIRouter, Request
from openai import OpenAI

from recruit_tracker_api.constants import MONGO_URL as url
from recruit_tracker_api.constants import OPENAI_API_KEY
from recruit_tracker_api.mongo import init_mongo

student_router = APIRouter()

client = OpenAI(api_key=OPENAI_API_KEY)


@student_router.get("/student/...")
async def read():
    ...


@student_router.get("/student/create")
async def create(request: Request):
    json = await request.json()

    client = init_mongo(url)


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
