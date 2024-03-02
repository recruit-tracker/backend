from pymongo import MongoClient


def init_mongo(url: str):
    """Init a mongo instance"""
    return MongoClient(host="localhost", port=27017)
