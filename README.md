# CPSC-449-Final-Project
An online bookstore API that allows users to view, search, and purchase books. The API will be built using FastAPI and the book data will be stored in MongoDB.

## How to run
1. Install Python 3.10
2. Install mongodb
3. Install uvicorn[standard], fastapi, pydantic, pymongo `py -m pip install uvicorn[standard] fastapi pydantic pymongo`
4. Insert bookstore.json in a collection and database in mongodb.
5. Run this program `py -m uvicorn main:app`
6. Go to http://localhost:8000/docs for the FastAPI doc thing to test this API **OR** use [Postman Client](https://www.postman.com/downloads/) to connect to http://localhost:8000

## Contributors
Ronald Lee, Chandra Lindy, Linh Nguyen