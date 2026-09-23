# 自定义响应数据类型，由Pydantic约束API输出格式
# 如果返回了规定外的字段被自动丢弃；如果缺少必填字段，会报错

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# 实体类新闻：id、title、content
# 必须继承 BaseModel，否则只是一个普通类，FastAPI 无法把它当作响应模型
class News(BaseModel):
    id: int
    title: str
    content: str

@app.get("/news/{id}", response_model=News)
async def get_news(id: int):
    # 实际项目中从数据库根据id查新闻
    # 假设数据库新闻id为1~6
    news_id = [1, 2, 3, 4, 5, 6]
    # 判断id是否在新闻id列表中，如果不在则抛出404异常
    if id not in news_id:
        raise HTTPException(status_code=404, detail="News not found")

    return {
        "id": id,
        "title": f"这是第{id}条新闻",
        "content": "新闻内容"
    }



