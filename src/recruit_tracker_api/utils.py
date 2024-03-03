
import hashlib, requests
import tempfile

import csv
import hashlib

import json
from datetime import datetime, timedelta
import csv, base64, bcrypt, jwt, io
from bson.objectid import ObjectId
import fitz, PyPDF2

GPT_API_ENDPOINT = 'https://api.openai.com/v1/engines/davinci-codex/completions'

from recruit_tracker_api.constants import OPENAI_API_KEY as GPT_KEY

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from gridfs import GridFS
from pymongo import MongoClient

from recruit_tracker_api.constants import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(user: dict, db):
    user_collection = db["users"]
    found_user = user_collection.find_one({"email": user["email"]})

    print(found_user)

    to_encode = {"role": found_user["role"], "email": found_user["email"]}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(create_jwt_token)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("email")
        role: str = payload.get("role")  # Extract the "role" claim
        if username is None or role is None:
            raise credentials_exception
        token_data = {"email": username, "role": role}
    except jwt.PyJWTError:
        raise credentials_exception
    return token_data


def decode_role(current_user: dict = Depends(get_current_user)):
    return current_user.get("role")


def store_pdf(db, pdf, email):
    fs = GridFS(db, collection="pdfs")  # Use a custom collection for PDFs

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(pdf.read())
            tmp.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    return fs.put(open(tmp.name, "rb"), metadata={"user_email": email})


def binary_to_pdf(binary_data):
    pdf_data = base64.b64decode(binary_data)
    pdf_buffer = io.BytesIO(pdf_data)

    return pdf_buffer


# def send_pdf_to_gpt(pdf_content, gpt_max_tokens=2000):
#     # Encode the PDF content as base64
#     # pdf_base64 = base64.b64encode(pdf_content)

#     # jsn_text = json.loads(pdf_content)
#     # files = {"file": jsn_text}

#     # Prepare the data payload
#     # payload = {
#     #     "prompt": gpt_prompt,
#     #     "max_tokens": gpt_max_tokens,
#     #     # "file": pdf_base64  # Include the base64-encoded PDF content
#     # }

#     # headers = {
#     #     "Content-Type": "application/json",
#     #     "Authorization": f"Bearer {GPT_KEY}",
#     # }

#     try:
#         # Make the request to GPT-3.5 with the PDF file
#         response = requests.post(GPT_API_ENDPOINT, files=files, headers=headers, json=payload)

#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"### BAD NEWS ### {response.status_code}")
#             return response.json()

#     except requests.RequestException as e:
#         print(f"Error in sending PDF to GPT: {e}")
#         return None

def csv_to_json(csv_file_path):
    json_data = []

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print(row)
            json_data.append(row)

    return json_data

def binary_to_text(pdf_binary_data):
    try:
        # Create a PyMuPDF document from the binary data
        pdf_document = fitz.open(stream=pdf_binary_data, filetype="pdf")
        
        text = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text()

        return text

    except Exception as e:
        # Handle exceptions, such as invalid PDF format
        print(f"Error converting PDF to text: {e}")
        return None
