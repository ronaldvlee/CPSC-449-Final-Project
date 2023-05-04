from typing import Union
from bson import ObjectId

from fastapi import FastAPI
from pydantic import BaseModel

from pymongo import MongoClient


import json

# Book Model: You will create a Pydantic model for the book data that includes the following fields: title, author, description, price, and stock.
class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int

# Custom Encoder to serialize ObjectId
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

app = FastAPI()
client = MongoClient("localhost", 27017)
collection = client.get_database('books').get_collection('books')

# Asynchronous Programming: All database operations should be done asynchronously to ensure the API remains responsive and performant.
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def retrieve_all_books():
    documents = []
    cursor = collection.find({})

    for document in cursor:
        documents.append(json.dumps(document, cls=CustomEncoder))

    return documents

# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def retrieve_book(book_id: int):
    return {"book_id": book_id}

# POST /books: Adds a new book to the store
@app.post("/books")
async def add_book():
    return

# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: int):
    return

# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    return

# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search")
async def search():
    return