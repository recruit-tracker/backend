import csv
import hashlib
import json
from datetime import datetime, timedelta

import bcrypt
import jwt
from bson.objectid import ObjectId
from fastapi import Depends, HTTPException
# from site_api.routes.models.Models import User
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

    sha256 = hashlib.sha256()
    sha256.update(pdf)
    file_hash = sha256.hexdigest()

    fs.put(pdf, metadata={"hash": file_hash, "user_email": email})
    return file_hash


def csv_to_json(csv_file_path):
    json_data = []

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print(row)
            json_data.append(row)

    return json_data
