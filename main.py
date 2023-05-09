from typing import Optional
from bson import ObjectId

from fastapi import FastAPI
from pydantic import BaseModel, validator

from motor.motor_asyncio import AsyncIOMotorClient

import json

# Load the config file

with open("config.json") as json_data_file:
    cfg = json.load(json_data_file)

# Book Model: You will create a Pydantic model for the book data that includes the following fields: title, author, description, price, and stock.
class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int

    # Validation for price to keep it as positive
    @validator('price')
    def price_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('Price must be positive')
        return value

    # Validation for stock to keep it as positive
    @validator('stock')
    def stock_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('Stock must be non-negative')
        return value

# Custom Encoder to serialize ObjectId, since json.dumps doesn't know what to do with the ObjectId object.
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

app = FastAPI()
client = AsyncIOMotorClient(cfg['mongodb']['connection_str'])
db = client[cfg['mongodb']['database_name']]
collection = db[cfg['mongodb']['collection_name']]

# Asynchronous Programming: All database operations should be done asynchronously to ensure the API remains responsive and performant.

# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def retrieve_all_books():
    documents = []
    cursor = collection.find({}) # find() does no I/O and does not require an await expression
                                 # the query is actually executed on the server when executing
                                 # an async for loop
                                 # source: https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#querying-for-more-than-one-document

    async for document in cursor:
        documents.append(json.dumps(document, cls=CustomEncoder))

    return documents

# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def retrieve_book(book_id: str):
    cursor = await collection.find_one(ObjectId(book_id))

    return [str(cursor).replace('\'', '\"')] # This is done to have parity with the output of json.dumps

# POST /books: Adds a new book to the store
@app.post("/books")
async def add_book(book: Book):
    book_dict = book.dict() # Since the parameter we are passing is type Book, there is no need for 
                            # additional validation, as pydantic already implements this for us.
    await collection.insert_one(book_dict)
    return {"message": "Book created successfully"}

# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    # Convert the book_id parameter to a ObjectId
    object_id = ObjectId(book_id)

    # Update the corresponding book in the database
    update_result = await collection.update_one({"_id": object_id}, {"$set": book.dict()})

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
    delete_result = await collection.delete_one({"_id": object_id})

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
    search_results = collection.find(query) # Same thing here, the query not executed until 
                                            # the async for so no await is needed

    # Convert the search results to a list of Book objects
    books = []
    async for result in search_results:
        book = json.dumps(result, cls=CustomEncoder)
        books.append(book)

    return books