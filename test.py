import requests

url = "http://localhost:5000/student"
with open("pdfs/test.pdf", "r") as f:
    pdf = f.read()

user = {"user": {"email": "test@test.com", "password": "wa", "resume": pdf}}

requests.post(url, json=user)
