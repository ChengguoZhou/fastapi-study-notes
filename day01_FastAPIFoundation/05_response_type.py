# 响应类型：JsonResponse（默认）、HTMLResponse
#         PlainTextResponse（纯文本）、FileResponse
#         StreamingResponse（流式响应）、RedirectResponse（重定向）

# 设置相应类型分为：1、装饰器指定响应类 `@app.get("/html", response_class=HTMLResponse)`
#               2、返回响应对象 `return FileResponse(path)`


from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
app = FastAPI()

#=========== 响应html格式===============
@app.get("/html", response_class=HTMLResponse)
def get_html():
    html_text = "<h1>Hello, FastAPI!</h1>"
    return html_text

#=========== 响应文件格式===============
@app.get("/file", response_class=FileResponse)
def get_html():
    pic_path = "./file/1.jpeg"
    return pic_path
