"""
课程中的中间件只是为了了解中间件“洋葱模型”，我用gpt写了实际开发场景的代码
"""
import logging
import time
import uuid
from asyncio import sleep

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s|%(message)s", force=True)

app = FastAPI()


# ① 请求ID：给每个请求打上唯一标识，方便串联日志排查
@app.middleware("http")
async def mw_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:8]
    request.state.request_id = rid  # 塞进 state，路由里能读
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid  # 回写给客户端
    return response


# ② 访问日志 + 耗时：记录每个请求的耗时，排查慢接口
@app.middleware("http")
async def mw_access_log(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
    finally:
        cost_ms = (time.perf_counter() - start) * 1000
        logging.info("%s %s -> %s  %.1fms  rid=%s", request.method, request.url.path,
                     status, cost_ms, getattr(request.state, "request_id", "-"))
    response.headers["X-Process-Time"] = f"{cost_ms:.1f}ms"
    return response


# ③ 统一异常处理：把 500 的默认纯文本换成统一 JSON 结构
@app.middleware("http")
async def mw_catch_exception(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error("!!! mw_catch_exception: %s: %s", type(e).__name__, e)
        return JSONResponse(status_code=500,
                            content={"code": 500, "msg": "server error", "data": None})


# ================= 测试接口 =================
@app.get("/ok")
async def ok(request: Request):
    return {"message": "Hello World", "rid": getattr(request.state, "request_id", None)}


@app.get("/slow")
async def slow():
    await sleep(1)  # 故意慢 1 秒，用来验证耗时统计
    return {"message": "slow done"}


@app.get("/boom")
async def boom():
    raise ValueError("boom in route")  # 未捕获异常 -> 应该走统一异常


@app.get("/notfound")
async def notfound():
    raise HTTPException(status_code=404, detail="no such book")  # 应该保持 404


@app.post("/echo")
async def echo(payload: dict):
    return {"received": payload}
