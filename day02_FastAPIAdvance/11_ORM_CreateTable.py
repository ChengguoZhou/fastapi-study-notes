"""
建表的骨架，后面会复用
"""
from datetime import datetime

from fastapi import FastAPI
from sqlalchemy import DateTime, String, Float, Integer, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

# 1.创建异步引擎
ASYNC_DB_URL = "mysql+aiomysql://root:root@localhost:3306/fastapi_demo?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,  # 输出 SQL 日志，生成 ORM 生成了什么 SQL日志
    pool_size=10,  # 连接池活跃连接数
    max_overflow=20  # 允许额外溢出的连接数
)


# 2.定义模型类：基类（公共字段） + 表模型类
# 基类

# 注意:onupdate=func.now() SQLAlchemy的Mysql不会自动生成on update current_timestamp子句
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间")


# 模型类
class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")


# 3.建表 定义函数建表 → FastAPI 启动的时候调用建表的函数
async def create_tables():
    async with async_engine.begin() as conn:  # 获取异步引擎，创建事务 - 建表
        await  conn.run_sync(Base.metadata.create_all)  # Base 模型类的元数据创建


@app.on_event("startup")
async def startup_event():
    await create_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("11_ORM_CreateTable:app", host="127.0.0.1", port=8000, reload=True)
