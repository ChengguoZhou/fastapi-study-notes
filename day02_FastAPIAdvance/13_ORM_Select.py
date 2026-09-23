"""
连接数据库的骨架 + 搜索相关语句(包含搜索一条数据/所有数据)
"""
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import DateTime, text, Integer, String, Float, select, and_, or_, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
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


# 查询所有图书数据
@app.get("/book/books")
async def get_book_list(db: AsyncSession = Depends(get_database)):  # 采用依赖注入方式，每个请求拿到独立数据库会话
    # 查询全部
    result = await db.execute(select(Book))
    book = result.scalars().all()
    return book


# 按id查询图书数据
@app.get("/book/get_book/{book_id}")
async def get_book_list(book_id: int, db: AsyncSession = Depends(get_database)):  # 采用依赖注入方式，每个请求拿到独立数据库会话
    # 方法一：db.get 按主键取单条，速度快
    # book = await db.get(Book, book_id)

    # 方法二 select语句 大于、小于等情况修改Book.id == book_id部分即可
    result = await db.execute(select(Book).where(Book.id == book_id))
    # 辨析：scalar_one_or_none 命中一条/不命中，命中多条抛异常
    # scalars().first() 返回第一条数据，如果为空返回None
    # scalar_one() 只能返回1条数据，否则报错
    book = result.scalar_one_or_none()
    return book


# 模糊查询、逻辑查询、包含查询
def to_dict(b: Book) -> dict:
    return {"id": b.id, "bookname": b.bookname, "author": b.author,
            "price": b.price, "publisher": b.publisher}


def parse_ids(ids: str) -> list[int]:
    try:
        return [int(x) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail=f"ids 必须是逗号分隔的整数，收到: {ids!r}")


# ============ ① 主搜索接口：条件从 URL 传入，AND 组合 ============
@app.get("/book/search_book")
async def search_book(
        bookname: Optional[str] = Query(None, description="书名模糊匹配（自动前后加 %）"),
        author: Optional[str] = Query(None, description="作者模糊匹配，% 任意个字符、_ 一个字符"),
        min_price: Optional[float] = Query(None, ge=0, description="价格下限"),
        max_price: Optional[float] = Query(None, ge=0, description="价格上限"),
        ids: Optional[str] = Query(None, description="id 列表，逗号分隔，如 1,3,5,7"),
        order_by: str = Query("id", pattern="^(id|price)$", description="排序字段"),
        desc: bool = Query(False, description="是否倒序"),
        limit: int = Query(20, ge=1, le=100, description="返回条数上限"),
        db: AsyncSession = Depends(get_database),
):
    conds = []
    if bookname:
        conds.append(Book.bookname.like(f"%{bookname}%"))
    if author:
        conds.append(Book.author.like(author))
    if min_price is not None:
        conds.append(Book.price >= min_price)
    if max_price is not None:
        conds.append(Book.price <= max_price)
    if ids:
        conds.append(Book.id.in_(parse_ids(ids)))

    stmt = select(Book)
    if conds:
        stmt = stmt.where(and_(*conds))  # 所有条件 AND

    col = Book.price if order_by == "price" else Book.id
    stmt = stmt.order_by(col.desc() if desc else col.asc()).limit(limit)

    result = await db.execute(stmt)
    return [to_dict(b) for b in result.scalars().all()]


# ============ ② OR 组合（对应课件的 & | 与非） ============
@app.get("/book/search_book/or")
async def search_or(
        author: Optional[str] = Query(None, description="作者模糊匹配（需手动添加%）"),
        min_price: Optional[float] = Query(None, description="价格大于"),
        db: AsyncSession = Depends(get_database),
):
    conds = []
    if author:
        conds.append(Book.author.like(author))
    if min_price is not None:
        conds.append(Book.price > min_price)
    if not conds:
        raise HTTPException(status_code=422, detail="author 和 min_price 至少要给一个")
    result = await db.execute(select(Book).where(or_(*conds)))
    return [to_dict(b) for b in result.scalars().all()]


# ============ ③ 路径参数版本（真正"通过路径"传搜索变量） ============
@app.get("/book/search_book/author/{author_name}")
async def search_by_author_path(author_name: str, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.author.like(f"%{author_name}%")))
    return [to_dict(b) for b in result.scalars().all()]


# ============ 聚合查询 （func.* 覆盖 count / max / min / sum / avg）============
@app.get("/book/count")
async def get_count(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(func.sum(Book.price)))
    return result.scalar()  # 提取单个标量值


# ============ 分页查询============
@app.get("/book/get_page")
async def get_page(page: int = Query(1, ge=1, description="页码(必须大于等于1，默认为1)"),
                   page_size: int = Query(3, gt=1, le=100, description="每页数据量（必须大于等于1，默认为3）"),
                   db: AsyncSession = Depends(get_database)):
    skip = (page - 1) * page_size
    # offset:跳过多少条； limit：每页多少条
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("13_ORM_Select:app", host="127.0.0.1", port=8000, reload=True)
