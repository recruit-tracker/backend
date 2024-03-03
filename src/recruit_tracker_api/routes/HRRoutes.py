# PDM
import base64
from fastapi import APIRouter, HTTPException, Request
import gridfs, PyPDF2, io
import openai, os
from starlette.responses import JSONResponse
import csv, json, pymongo, jwt
import recruit_tracker_api.utils as utils
from recruit_tracker_api.constants import OPENAI_API_KEY
from recruit_tracker_api.constants import MONGO_URL as url
from recruit_tracker_api.mongo import init_mongo
import pdfplumber

openAI_client = openai.OpenAI(api_key=OPENAI_API_KEY)


hr_router = APIRouter()


@hr_router.get("/hr")
async def root():
    return {"message": "FAST!"}

from fastapi.responses import JSONResponse

@hr_router.post("/hr/import")
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


@hr_router.post("/hr/suggestion")
async def prompt_gpt(request: Request):
    try:
        json_data = await request.json()
        user_email = json_data.get("email")

        if user_email:
            client = init_mongo(url)
            db = client["recruit_tracker"]
            user_collection = db["users"]

            pdf_ID = user_collection.find_one({"email": user_email}).get("pdf_ID")

            fs = gridfs.GridFS(db, collection="pdfs")

            try:
                # Retrieve file from GridFS
                file_obj = fs.get(pdf_ID)
                # Read PDF content
                with pdfplumber.open(file_obj) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()

                prompt = "Rate this resume on a scale of 1-10 based on criteria like format, human readability, and other relevant info. Be objective about the resume - do not use personal pronouns. Respond with a few concise recommendations."
                prompt2 = "You are a staff member in charge of hiring a software engineer. Based on this resume, how likely (out of 10) are they to get a job based on the resume?, "
                
                # Use OpenAI API to interact with GPT-3.5 Turbo
                completion = openAI_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": prompt2,
                        },
                        {
                            "role": "user",
                            "content": text,  # Use the extracted user input
                        },
                    ],
                )

                response_text = completion.choices[0].message  # Extract the text from the completion

                return {"text": response_text}

            except Exception as e:
                raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    


def bytes_to_utf8(pdf_bytes):
    try:
        # Create a PyPDF2 PdfReader object from the binary PDF data
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        # Initialize an empty string to store the extracted text
        text = ""

        # Iterate through each page and extract text
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text += page.extractText()

        # Encode the text as UTF-8
        utf8_encoded_text = text.encode("utf-8")

        return utf8_encoded_text
    except Exception as e:
        print(f"Error processing PDF file: {str(e)}")
        return None

