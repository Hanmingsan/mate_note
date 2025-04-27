
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return{"message": "hello world!"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return{"itemid": item_id + 'love u'}
