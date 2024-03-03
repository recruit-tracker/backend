import hashlib

import bcrypt
from bson.objectid import ObjectId
from gridfs import GridFS
from pymongo import MongoClient


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def store_pdf(db, pdf):
    fs = GridFS(db, collection="pdfs")  # Use a custom collection for PDFs

    sha256 = hashlib.sha256()
    sha256.update(pdf.encode())
    file_hash = sha256.hexdigest()

    fs.put(pdf.encode(), metadata={"hash": file_hash})
    return file_hash
