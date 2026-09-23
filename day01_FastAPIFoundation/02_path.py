from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/book/{id}")
async def get_book(id: int = Path(..., gt=0, lt=101)):
    return {"id": id, "title": f"这是第{id}本书"}