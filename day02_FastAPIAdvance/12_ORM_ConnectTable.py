"""
连接数据库的骨架
建表的骨架，后面添加会话与依赖项
后面会复用
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("12_ORM_ConnectTable:app", host="127.0.0.1", port=8000, reload=True)
