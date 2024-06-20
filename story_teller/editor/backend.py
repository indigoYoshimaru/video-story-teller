# backend.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import urllib.parse

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['text_editor']
collection = db['posts']

app = FastAPI()

class Post(BaseModel):
    post_id: str
    post_title: str
    vietnamese: str
    english: str

@app.get("/post/{post_id}")
async def get_post(post_id: str):
    post = collection.find_one({"post_id": post_id})
    if post:
        post["vietnamese"] = urllib.parse.unquote(post["vietnamese"])
        return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/post")
async def upsert_post(post: Post):
    post_data = post.dict()
    post_data["vietnamese"] = urllib.parse.quote(post_data["vietnamese"].strip())
    collection.update_one({"post_id": post.post_id}, {"$set": post_data}, upsert=True)
    return {"message": "Data written to MongoDB"}

@app.get("/posts")
async def get_posts():
    posts = collection.find({"status": 1})
    return [{"post_id": post["post_id"], "post_title": post["post_title"]} for post in posts]