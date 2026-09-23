"""
删除图书数据
"""
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import DateTime, text, Integer, String, Float, select, and_, or_, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

# ============= 定义Book实体类：基类（公共字段） + 表模型类===============
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


# Book 实体类
class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")

# ============= 定义Book DTO: BookUpdate===============
class BookUpdate(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str


# 1.创建异步引擎
ASYNC_DB_URL = "mysql+aiomysql://root:root@localhost:3306/fastapi_demo?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,  # 输出 SQL 日志，生成 ORM 生成了什么 SQL日志
    pool_size=10,  # 连接池活跃连接数
    max_overflow=20  # 允许额外溢出的连接数
)

# 新建局部异步会话
async_session_local = async_sessionmaker(
    bind=async_engine,  # 绑定引擎
    class_=AsyncSession,  # 指定会话类
    expire_on_commit=False  # 提交后对象不过期，避免再次查库
)


# 连接数据库
async def get_database():
    async with async_session_local() as session:
        try:
            yield session  # 请求进来时执行创建会话、交给路由函数
            await session.commit()  # 请求处理完后提交事务
        except:
            await session.rollback()  # 出异常，则回滚
            raise  # raise作用：把原始异常抛出，让报错指向真正错误位置
        finally:
            await session.close()  # 不管是否异常，都要关闭会话

# ============== 修改图书==============
@app.delete("/book/delete/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    # 先查后删，最后自提交
    db_book = await db.get(Book, book_id)

    if db_book is None:
        raise HTTPException(status_code=404, detail="查无次数")

    await db.delete(db_book)
    await db.commit()
    return {"msg": "删除图书成功！"}

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("16_ORM_Delete:app", host="127.0.0.1", port=8008, reload=True)
