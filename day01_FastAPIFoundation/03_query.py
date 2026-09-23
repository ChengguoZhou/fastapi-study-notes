from importlib import reload

from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/news/news_list")
async def get_news_list(
        skip: int = Query(0, description="跳过的记录数"),
        limit: int = Query(10, description="一页记录数")
):
    return {"skip": skip, "limit": limit}

# 点启动能直接运行 或者 控制台敲命令"uvicorn 03_query:app --reload"
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "03_query:app",
            host="127.0.0.1",
            port=8000,
            reload=True
    )

