# CPSC-449-Final-Project

An online bookstore API that allows users to view, search, and purchase books. The API will be built using FastAPI and the book data will be stored in MongoDB.

## How to run

1. Install [Python](https://www.python.org/) and [MongoDB](https://www.mongodb.com/)
2. Clone this repo `git clone https://github.com/ronaldvlee/CPSC-449-Final-Project.git`
3. Change directory `cd CPSC-449-Final-Project`
4. Install uvicorn\[standard\], fastapi, pydantic, pymongo, and motor `py -m pip install 'uvicorn[standard]' fastapi pydantic pymongo motor`
5. Insert `bookstore.json` (or your own book database) in a collection and database in MongoDB.
6. Change `config.json`'s variables to your appropriate connection string, database name, and collection name.
7. Run this program `py -m uvicorn main:app` _dev-mode: add `--reload` flag_
8. Go to http://localhost:8000/docs for the FastAPI doc thing to test this API **OR** use [Postman Client](https://www.postman.com/downloads/) to connect to http://localhost:8000/

## Contributors

Ronald Lee, Chandra Lindy, Linh Nguyen
