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
    sales: int

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
    
    # Validation for sales to keep it as positive
    @validator('sales')
    def sales_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('Sales must be non-negative')
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
    try:
        async for document in cursor:
            documents.append(json.dumps(document, cls=CustomEncoder))
    except Exception as e:
        return {'error': str(e)}

    return {'books': documents}

# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def retrieve_book(book_id: str):
    try: 
        cursor = await collection.find_one(ObjectId(book_id))
        return {'books': [str(cursor).replace('\'', '\"')]} # This is done to have parity with the output of json.dumps
    except Exception as e:
        return {'error': str(e)}

# POST /books: Adds a new book to the store
@app.post("/books")
async def add_book(book: Book):
    book_dict = book.dict() # Since the parameter we are passing is type Book, there is no need for 
                            # additional validation, as pydantic already implements this for us.
    try: 
        await collection.insert_one(book_dict)
        return {"message": "Book created successfully"}
    except Exception as e:
        return {"error": str(e)}

# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    # Convert the book_id parameter to a ObjectId
    object_id = ObjectId(book_id)

    # Update the corresponding book in the database
    try:
        update_result = await collection.update_one({"_id": object_id}, {"$set": book.dict()})
    except Exception as e:
        return {"error": str(e)}

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
    try:
        delete_result = await collection.delete_one({"_id": object_id})
    except Exception as e:
        return {"error": str(e)}

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
    try:
        async for result in search_results:
            book = json.dumps(result, cls=CustomEncoder)
            books.append(book)
    except Exception as e:
        return {'error': str(e)}

    return {'books': books}


# Aggregation

@app.get("/total")
async def get_total_books():
    try:
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$stock"}}}]
        result = await collection.aggregate(pipeline).to_list(1)
        total_books = result[0]["total"]
        return {"total_books": total_books}
    except IndexError:
        return {"error": "No books found in the database."}
    except Exception as e:
        return {"error": str(e)}

# Retrieve data of the top 5 best selling books
@app.get("/bestsellers")
async def get_bestsellers():
    # Define the aggregation pipeline
    pipeline = [
        { "$sort": { "sales": -1 } },
        { "$limit": 5 },
        { "$project": { "_id": 0, "title": 1, "author": 1, "description": 1, "price": 1, "stock": 1, "sales": 1 } }
    ]
    # Execute the aggregation and return the results
    try:
        results = await collection.aggregate(pipeline).to_list(None)
        return {"bestsellers": results}
    except Exception as e:
        return {"error": str(e)}


# Retrieve data of the top 5 authors with the most books in the store
@app.get("/top_authors")
async def get_top_authors():
    # Define the aggregation pipeline
    pipeline = [
        {"$group": {"_id": "$author", "total_stock": {"$sum": "$stock"}}},
        {"$sort": {"total_stock": -1}},
        {"$limit": 5}
    ]
    try:
        # Execute the aggregation and return the results
        top_authors = await collection.aggregate(pipeline).to_list(None)
        return {"top_authors": top_authors}
    except Exception as e:
        return {"error": str(e)}


# Indexing
# Create a function startup() to be called when the app starts up, in which we create indexes for the collection
@app.on_event("startup")
async def startup():
    # Create an index on the "title" field
    await collection.create_index('title')

    # Create a compound index on the "author" and "stock" fields
    await collection.create_index([('author', 1), ('stock', -1)])

    # Create a descending index on the "sales" field
    await collection.create_index([('sales', -1)])