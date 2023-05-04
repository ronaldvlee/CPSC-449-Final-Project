from typing import Optional
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
async def retrieve_book(book_id: str):
    documents = []
    cursor = collection.find({'_id': ObjectId(book_id)})

    for document in cursor:
        documents.append(json.dumps(document, cls=CustomEncoder))

    return documents

# POST /books: Adds a new book to the store
@app.post("/books")
async def add_book(book: Book):
    book_dict = book.dict()
    collection.insert_one(book_dict)
    return {"message": "Book created successfully"}

# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    # Convert the book_id parameter to a ObjectId
    object_id = ObjectId(book_id)

    # Update the corresponding book in the database
    update_result = collection.update_one({"_id": object_id}, {"$set": book.dict()})

    # Check if the book was found and updated
    if update_result.modified_count == 1:
        return {"message": "Book updated successfully"}
    else:
        return {"message": "Book not found"}


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    # Convert the book_id parameter to a ObjectId
    object_id = ObjectId(book_id)

    # Delete the corresponding book from the database
    delete_result = collection.delete_one({"_id": object_id})

    # Check if the book was found and deleted
    if delete_result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    else:
        return {"message": "Book not found"}

# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search")
async def search_books(title: Optional[str] = None, author: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    # Construct the query object based on the search parameters
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"} # Case-insensitive search using regex
    if author:
        query["author"] = {"$regex": author, "$options": "i"} # Case-insensitive search using regex
    if min_price:
        query["price"] = {"$gte": min_price}
    if max_price:
        query["price"] = {"$lte": max_price}
    if min_price and max_price:
        query["price"] = {"$gte": min_price, "$lte": max_price}

    # Execute the search query and retrieve the results
    search_results = collection.find(query)

    # Convert the search results to a list of Book objects
    books = []
    for result in search_results:
        book = Book(**result)
        books.append(book)

    # Check if any books were found
    # if len(books) == 0:
    #     raise HTTPException(status_code=404, detail="No books found")

    return books