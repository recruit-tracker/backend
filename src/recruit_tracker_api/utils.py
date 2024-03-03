import hashlib
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


class Student:
    username = str
    ...


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_jwt_token(user: dict):
    to_encode = user.copy()
    to_encode["role"] = user.get("role")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(create_jwt_token)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")  # Extract the "role" claim
        if username is None or role is None:
            raise credentials_exception
        token_data = {"sub": username, "role": role}
    except jwt.PyJWTError:
        raise credentials_exception
    return token_data


async def decode_role(current_user: dict = Depends(get_current_user)):
    return current_user.get("role")

    # user = {
    #     id: 1,
    #     "name": "Mitchell Kimbell",
    #     "email": "mfkimbell@gmail.com",
    #     "password": "immfkingbell",
    #     "phone": "2053128982",
    #     "state": "AL",
    #     "school": "University of Alabama at Birmingham",
    #     "graduation": "05/2024",
    #     "position": "Intern",
    #     "officeLocation": "Birmingham",
    #     "stage": "first-round",
    #     "interest": 8,
    #     "linkedIn": "https://www.linkedin.com/in/mitchell-kimbell-mscs-3384191a1/",
    #     "feedback": "This person was annoying"
    #   }

    # tok = create_jwt_token(user)
    # print(tok)
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def store_pdf(db, pdf):
    fs = GridFS(db, collection="pdfs")  # Use a custom collection for PDFs

    sha256 = hashlib.sha256()
    sha256.update(pdf.encode())
    file_hash = sha256.hexdigest()

    fs.put(pdf.encode(), metadata={"hash": file_hash})
    return file_hash
