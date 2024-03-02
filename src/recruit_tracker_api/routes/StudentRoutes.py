# PDM
import requests
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from starlette.responses import JSONResponse

from recruit_tracker_api.constants import OPENAI_API_KEY

student_router = APIRouter()


@student_router.get("/")
async def root():
    return {"message": "FAST!"}


client = OpenAI(api_key=OPENAI_API_KEY)


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
