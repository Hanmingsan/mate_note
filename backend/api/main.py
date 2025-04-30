
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return{"message": "hello world!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return{"itemid": item_id + 114514}

@app.get("/search_student_by_name/{name}")
async def search_student_by_name(name: str):
    return{name}
