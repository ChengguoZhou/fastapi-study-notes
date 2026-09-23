from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class User(BaseModel):
    username: str = Field(
        default="张三",
        min_length=2,
        max_length=10,
        description="用户名，长度要求2-10个字"
    )
    password: str = Field(min_length=3, max_length=20,
                          description="密码，长度3-20个字符")

@app.get("/register")
async def register(user: User):
    return user

# 点启动能直接运行 或者 控制台敲命令"uvicorn 04_response_body:app --reload"
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "04_response_body:app",
            host="127.0.0.1",
            port=8000,
            reload=True
    )