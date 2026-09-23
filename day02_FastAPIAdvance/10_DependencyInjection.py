"""
依赖注入
"""
from fastapi import FastAPI, Query, Depends

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# 1.依赖项：分页参数逻辑抽出来共用
async def common_parameter(skip: int = Query(0, ge=0),
                           limit: int = Query(10, le=60)):
    return {"skip": skip, "limit": limit}


# 2.声明依赖项 → 依赖注入
@app.get("/news/news_list")
async def get_news_list(commons=Depends(common_parameter)):
    return commons


@app.get("/user/user_list")
async def get_user_list(commons=Depends(common_parameter)):
    return commons
