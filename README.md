# CPSC-449-Final-Project
An online bookstore API that allows users to view, search, and purchase books. The API will be built using FastAPI and the book data will be stored in MongoDB.

## How to run
1. Install [Python](https://www.python.org/)
2. Install [MongoDB](https://www.mongodb.com/)
3. Clone this repo `git clone https://github.com/ronaldvlee/CPSC-449-Final-Project.git`
4. Change directory `cd CPSC-449-Final-Project`
5. Install uvicorn\[standard\], fastapi, pydantic, and pymongo `py -m pip install uvicorn[standard] fastapi pydantic pymongo`
6. Insert bookstore.json (or your own book database) in a collection and database in MongoDB.
7. Run this program `py -m uvicorn main:app` *dev-mode: add `--reload` flag*
8. Go to http://localhost:8000/docs for the FastAPI doc thing to test this API **OR** use [Postman Client](https://www.postman.com/downloads/) to connect to http://localhost:8000/

## Contributors
Ronald Lee, Chandra Lindy, Linh Nguyen