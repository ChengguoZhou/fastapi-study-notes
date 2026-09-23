# 第一章 FastAPI 基础入门：从 0 配置项目到写出第一个接口

> 适用对象：会一点点 Python（函数、装饰器、类型注解），但没写过 Web 接口的初学者。
> 本章目标：能独立创建项目 → 运行项目 → 写出「路由 + 路径参数 + 查询参数 + 请求体 + 响应类型 + 自定义响应格式」的完整小服务。

---

## 0. 本章地图（对应讲义 `第一章_FastAPI入门.pdf` 的目录）

讲义封面标题：**FastAPI 基础入门 —— 基础程序、路由、请求与响应**

| 序号 | 讲义板块 | 具体内容 | 对应示例代码 |
| --- | --- | --- | --- |
| 1 | FastAPI 框架基础 | 第一个 FastAPI 程序、FastAPI 是什么、同步与异步、三大特点（性能高 / 开发效率高 / 自动生成文档）、Pydantic 校验、可交互式文档 | `代码/01-路由.py` |
| 2 | 使用 FastAPI 框架搭建 Web 服务 | 1. 创建项目（FastAPI 框架、虚拟环境）<br>2. 运行项目（run 项目、`uvicorn main:app --reload`）<br>3. 访问项目（访问路由、访问交互式文档 `/docs`） | `main.py` |
| 3 | 路由 | 路由 = URL 地址与处理函数之间的映射；装饰器写法 | `代码/01-路由.py` |
| 4 | 参数 | 参数分类（路径参数 / 查询参数 / 请求体） | — |
| 4.1 | 路径参数 | 基本路径参数 + `Path` 类型注解 | `代码/02-路径参数.py` |
| 4.2 | 查询参数 | 基本查询参数 + `Query` 类型注解 | `代码/03-查询参数.py` |
| 4.3 | 请求体参数 | HTTP 请求三部分、`BaseModel` 定义类型 + `Field` 类型注解 | `代码/04-请求体参数.py` |
| 5 | 请求与响应 | 响应类型总览（JSON / HTML / 纯文本 / 文件 / 流 / 重定向）、设置响应类型的两种方式 | — |
| 5.1 | 响应类型 - JSON 格式 | 默认行为（`jsonable_encoder` + `JSONResponse`） | `代码/01-路由.py` |
| 5.2 | 响应 HTML 格式 | `response_class=HTMLResponse` | `代码/05-响应类型-HTML格式.py` |
| 5.3 | 响应文件格式 | 返回响应对象 `FileResponse` | `代码/06-响应类型-文件格式.py` |
| 5.4 | 自定义响应数据格式 | `response_model` 约束输出结构 | `代码/07-自定义响应数据格式.py` |
| 6 | 异常处理 | `HTTPException` 返回标准 4xx 错误 | 见 §11 |

**建议学习顺序**：§1 → §2 → §3 → §4 → §5 → §6 → §7 → §8 → §9 → §10 → §11，每节都「先看概念 → 再跑代码 → 最后做练习」。

---

## 1. 学前准备

### 1.1 环境检查

打开终端（Windows 用 PowerShell / CMD，macOS 用 Terminal），执行：

```bash
python --version
# 期望输出：Python 3.8 及以上（推荐 3.9 ~ 3.12）
```

如果提示找不到 `python`，试试：

```bash
py --version        # Windows 专用启动器
python3 --version   # macOS / Linux
```

> ⚠️ 版本提醒：FastAPI 较新版本已不再支持 Python 3.6/3.7，请确保 ≥ 3.8。

### 1.2 先建立 4 个「是什么」（不需要背，混个眼熟）

| 名词 | 一句话解释 |
| --- | --- |
| **Web 框架** | 帮你处理 HTTP 请求/响应的工具库，你只写业务函数，剩下的路由、解析、序列化它全包了。 |
| **API 接口** | 一个网址（URL）+ 一种请求方法（GET/POST），你访问它，它返回数据（通常是 JSON）。 |
| **路由（Route）** | URL 地址 → 处理函数 的映射关系。决定「用户访问哪个网址时，服务器执行哪段代码」。 |
| **同步 vs 异步** | 同步：一个请求处理完才处理下一个；异步：遇到 I/O 等待时先去处理别的请求，所以吞吐量高。FastAPI 用 `async def` 支持异步。 |

讲义里用一段代码直观对比了两者耗时：

```python
# 同步：10 次 time.sleep(1) 串行 → 约 10 秒
@app.get("/sync")
def func_sync():
    start = time.time()
    for i in range(10):
        time.sleep(1)
    return {"time": f"{time.time() - start:.2f}s"}

# 异步：10 个 asyncio.sleep(1) 并发 → 约 1 秒
@app.get("/async")
async def func_async():
    start = time.time()
    tasks = [asyncio.sleep(1) for i in range(10)]
    await asyncio.gather(*tasks)
    return {"time": f"{time.time() - start:.2f}s"}
```

### 1.3 FastAPI 的三大特点（讲义总结）

1. **性能高** —— 基于 Starlette + Pydantic，接近 Node.js / Go 的异步性能。
2. **开发效率高** —— 类型注解即校验，少写大量样板代码。
3. **自动生成文档** —— 写完代码就白送一套可交互 API 文档（`/docs`）。

---

## 2. 第一步：创建项目 + 虚拟环境

### 2.1 为什么要虚拟环境？

讲义原话：**隔离项目运行环境，避免依赖冲突，保持全局环境的干净和稳定。**

也就是说：A 项目要 fastapi 0.95，B 项目要 fastapi 0.110，如果都装到全局 Python 里必然打架。每个项目一个独立 `venv` 目录就互不干扰。

### 2.2 方式一：用 PyCharm（讲义演示方式）

1. 打开 PyCharm → `New Project`；
2. 左侧选择项目类型 `FastAPI`（如果没有就选 `Pure Python`，效果一样）；
3. `Location` 选好存储位置和项目名称，例如 `day01_FastAPI基础入门`；
4. 展开 `Python Interpreter` → 选择 `New environment (virtualenv)`，即**创建虚拟环境**（默认位置在项目下的 `venv/`）；
5. 点击 `Create`。

> 卡片顺序就是讲义上那行流程：**FastAPI → 存储位置及项目名称 → 创建虚拟环境 → Create**。

### 2.3 方式二：用命令行（推荐，任何编辑器都通用）

```bash
# 1) 进入你想放项目的目录
cd C:\Users\你的用户名\Desktop

# 2) 创建项目文件夹
mkdir day01_FastAPI基础入门
cd day01_FastAPI基础入门

# 3) 创建虚拟环境，名字叫 venv
python -m venv venv
```

**激活虚拟环境**（这步必须做，否则依赖会装到全局）：

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

激活成功的标志：终端提示符前面多了一个 `(venv)`。

> PowerShell 若报「禁止运行脚本」，先执行一次：
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2.4 建议的项目目录结构

和本仓库保持一致，初学阶段就够用了：

```
day01_FastAPI基础入门/
├── venv/                        # 虚拟环境（不用管，不要提交到 git）
├── 代码/                        # 按知识点拆分的示例代码
│   ├── 01-路由.py
│   ├── 02-路径参数.py
│   ├── 03-查询参数.py
│   ├── 04-请求体参数.py
│   ├── 05-响应类型-HTML格式.py
│   ├── 06-响应类型-文件格式.py
│   ├── 07-自定义响应数据格式.py
│   └── files/
│       └── 1.jpeg               # 06 用到的测试图片
├── main.py                      # 主程序（学习时可以先只放一个文件）
└── requirements.txt             # 依赖清单
```

> 💡 一个小坑：`06-响应类型-文件格式.py` 里的路径是 `./files/1.jpeg`，是**相对当前工作目录**的。
> 所以一定要 `cd 代码` 之后再运行，否则会报 `FileNotFoundError`。

---

## 3. 第二步：安装依赖

确认虚拟环境已激活（提示符有 `(venv)`），然后：

```bash
pip install fastapi "uvicorn[standard]"
```

各组件作用：

| 包 | 作用 |
| --- | --- |
| `fastapi` | 框架本体：路由、参数校验、自动文档 |
| `uvicorn` | ASGI 服务器，真正负责「监听端口、接收 HTTP 请求」 |
| `uvicorn[standard]` | 带高性能依赖（httptools、uvloop 等），推荐加上方括号 |
| `pydantic` | 随 fastapi 自动安装，负责数据模型和校验 |
| `python-multipart` | 只有用到表单/文件上传时才需要：`pip install python-multipart` |

导出依赖清单（方便换电脑复现）：

```bash
pip freeze > requirements.txt
# 换环境时：pip install -r requirements.txt
```

国内网络慢可以加镜像：

```bash
pip install fastapi "uvicorn[standard]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 4. 第三步：写第一个程序并运行

### 4.1 创建 `main.py`

```python
from fastapi import FastAPI

# 创建 FastAPI 实例，变量名建议就叫 app
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

拆解这 6 行：

- `FastAPI()`：创建应用对象，**必须叫 `app` 或后面启动命令里能对上名字**。
- `@app.get("/")`：装饰器，声明「GET 请求访问根路径 `/` 时，执行下面这个函数」。
- `async def root()`：处理函数，可以写成普通 `def`，也可以写 `async def`。
- `return {...}`：返回字典，FastAPI 自动转成 JSON 响应。

### 4.2 启动服务

在 `main.py` 所在目录执行：

```bash
uvicorn main:app --reload
# 或者（更稳，避免 PATH 问题）
python -m uvicorn main:app --reload
```

命令三段的含义（必记）：

| 部分 | 含义 |
| --- | --- |
| `main` | 模块名，即 `main.py`（不加 `.py`） |
| `app` | `main.py` 里那个 `FastAPI()` 实例的变量名 |
| `--reload` | 改代码后自动重启服务器，**开发阶段一定要加**；上线不要加 |

> 📌 讲义上写的 `uricorn main:app --reload` 是笔误，正确拼写是 **uvicorn**。

启动成功的输出大致是：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
```

停止服务：在终端按 `Ctrl + C`。

> 在 PyCharm 里也可以直接右键 `main.py` → `Run`（讲义称「run 项目」），本质就是替你执行了上面的命令。

### 4.3 访问项目（讲义第 3 步）

浏览器打开：

| 地址 | 作用 |
| --- | --- |
| http://127.0.0.1:8000/ | 访问路由，看到 `{"message":"Hello World"}` |
| http://127.0.0.1:8000/docs | **Swagger UI 交互式文档**，可直接点「Try it out」测试接口 |
| http://127.0.0.1:8000/redoc | ReDoc 风格的文档 |

`/docs` 是 FastAPI 送的大礼：你写的每个参数、每个校验规则都会自动出现在文档里。调试接口时优先用它。

---

## 5. 路由（对应 `代码/01-路由.py`）

### 5.1 概念

> **路由就是 URL 地址和处理函数之间的映射关系**，它决定了当用户访问某个特定网址时，服务器应该执行哪段代码来返回结果。

FastAPI 的路由定义基于 Python 的**装饰器模式**：`@app.请求方法("路径")`。

### 5.2 代码

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World888"}


# 访问 /hello，响应结果 {"msg": "你好 FastAPI"}
@app.get("/hello")
async def get_hello():
    return {"msg": "你好 FastAPI"}
```

### 5.3 常用请求方法装饰器

| 装饰器 | 用途 |
| --- | --- |
| `@app.get("/xxx")` | 查询数据 |
| `@app.post("/xxx")` | 新增数据（常配请求体） |
| `@app.put("/xxx")` | 全量更新 |
| `@app.delete("/xxx")` | 删除 |

### 5.4 运行验证

```bash
cd 代码
uvicorn 01-路由:app --reload   # 模块名含中文和数字时，若报错就改成英文文件名，如 route_demo.py
```

**建议**：把示例文件另存为英文名（如 `route_demo.py`）再运行，能躲开编码/模块名的一堆坑。

### 5.5 练习

> 需求：访问路径 `/user/hello`，响应结果是 `{ "msg": "我正在学习 FastAPI ......" }`

<details>
<summary>参考答案</summary>

```python
@app.get("/user/hello")
async def user_hello():
    return {"msg": "我正在学习 FastAPI ......"}
```
</details>

---

## 6. 参数总览：三类参数怎么选

写接口时，客户端往往会附带「额外信息和指令」，这就是参数。分类看「**位置**」：

| 类型 | 位置 | 作用 | 方法 | 例子 |
| --- | --- | --- | --- | --- |
| **路径参数** | URL 路径的一部分 | 指向唯一的、特定的资源 | GET | `/book/{id}` |
| **查询参数** | URL `?` 之后，`k1=v1&k2=v2` | 对资源集合做过滤、排序、分页 | GET | `/news/news_list?skip=0&limit=10` |
| **请求体参数** | HTTP 请求的消息体（body） | 创建、更新资源，携带大量 JSON 数据 | POST / PUT | `/register` + JSON |

一句话记忆：**路径参数定位「哪一个」，查询参数筛选「哪一批」，请求体参数提交「一整条」**。

---

## 7. 路径参数 + `Path` 类型注解（对应 `代码/02-路径参数.py`）

### 7.1 最基础的路径参数

用 `{}` 占位，函数同名形参接收，类型注解自动做转换和校验：

```python
@app.get("/book/{id}")
async def get_book(id: int):
    return {"id": id, "title": f"这是第{id}本书"}
```

访问 `/book/3` → `{"id":3,"title":"这是第3本书"}`。
访问 `/book/abc` → 自动返回 `422` 校验错误（因为 `abc` 不是 `int`），**不用你写一行 if 判断**。

### 7.2 用 `Path` 加更多约束

`id: int` 只保证是整数。若还想限制「必须大于 0、小于 101」，就用 `Path`：

```python
from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/book/{id}")
async def get_book(id: int = Path(..., gt=0, lt=101, description="书籍id，取值范围1-100")):
    return {"id": id, "title": f"这是第{id}本书"}


# 需求：查找书籍的作者，路径参数 name，长度范围 2-10
@app.get("/author/{name}")
async def get_name(name: str = Path(..., min_length=2, max_length=10)):
    return {"msg": f"这是{name}的信息"}
```

`Path` 常用参数（讲义表格）：

| 参数 | 含义 |
| --- | --- |
| `...`（Ellipsis） | 必填，不可省略 |
| `gt` / `ge` | 大于 / 大于等于 |
| `lt` / `le` | 小于 / 小于等于 |
| `min_length` / `max_length` | 字符串长度限制 |
| `description` | 参数说明，会显示在 `/docs` 里 |

### 7.3 练习

> 定义两个接口，都带路径参数并用 `Path` 做类型注解：
> ① 以「新闻分类 id」为参数，id 范围 1 ~ 100；
> ② 以「新闻分类名称」为参数，分类名称长度 2 ~ 10。

<details>
<summary>参考答案</summary>

```python
@app.get("/news/category/{id}")
async def get_category(id: int = Path(..., gt=0, lt=101, description="新闻分类id，1-100")):
    return {"id": id}


@app.get("/news/category_name/{name}")
async def get_category_name(name: str = Path(..., min_length=2, max_length=10)):
    return {"name": name}
```
</details>

---

## 8. 查询参数 + `Query` 类型注解（对应 `代码/03-查询参数.py`）

### 8.1 什么是查询参数

**声明的参数不是路径参数时，路径操作函数会把该参数自动解释为查询参数。**

它出现在 URL 的 `?` 之后，形如 `?skip=0&limit=10`，适合做分页、过滤、排序。

### 8.2 代码

```python
from fastapi import FastAPI, Query

app = FastAPI()


# 需求：查询新闻 → 分页，skip：跳过的记录数，limit：返回的记录数
@app.get("/news/news_list")
async def get_news_list(
    skip: int = Query(0, description="跳过的记录数", lt=100),
    limit: int = Query(10, description="返回的记录数")
):
    return {"skip": skip, "limit": limit}
```

关键点：

- `Query(0, ...)` 的第一个位置参数是**默认值**，写 0 表示「不传就按 0 处理」，即该参数**可选**。
- 若第一个位置参数写 `...`，则表示**必填**。
- 不写 `Query` 直接 `skip: int = 0` 也能用，但 `Query` 能附加 `gt/lt/min_length/description` 等校验与文档信息。

### 8.3 验证

- `/news/news_list` → `{"skip":0,"limit":10}`
- `/news/news_list?skip=5&limit=20` → `{"skip":5,"limit":20}`
- `/news/news_list?skip=200` → `422`，因为 `lt=100` 要求小于 100

### 8.4 练习

> 设计接口查询图书，携带两个查询参数：图书分类和价格。
> ① 图书分类：默认值为 `Python开发`，长度限制 5 ~ 255；
> ② 价格：大小范围 50 ~ 100。

<details>
<summary>参考答案</summary>

```python
@app.get("/book/search")
async def search_book(
    category: str = Query("Python开发", min_length=5, max_length=255, description="图书分类"),
    price: int = Query(..., ge=50, le=100, description="价格，50-100")
):
    return {"category": category, "price": price}
```
</details>

---

## 9. 请求体参数 + `BaseModel` / `Field`（对应 `代码/04-请求体参数.py`）

### 9.1 先复习 HTTP 请求的三部分

① **请求行**：方法、URL、协议版本
② **请求头**：元数据（`Content-Type`、`Authorization` 等）
③ **请求体**：实际要发送的数据内容 ← **请求体参数取的就是这里**

请求体参数用于**创建、更新资源**，能携带大量 JSON 数据，方法通常是 `POST` / `PUT`。

### 9.2 两步走：① 定义类型 ② 类型注解

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


# 注册：用户名和密码 → str
class User(BaseModel):
    username: str = Field(default="张三", min_length=2, max_length=10, description="用户名，长度要求2-10个字")
    password: str = Field(min_length=3, max_length=20)


@app.post("/register")
async def register(user: User):
    return user
```

要点：

- 继承 `BaseModel` 的类就是「请求体模型」，字段类型注解即自动校验/转换。
- 函数参数 `user: User` 是**模型类型注解**，FastAPI 会自动把请求体 JSON 解析成 `User` 对象。
- `Field` 负责字段级约束：

| 参数 | 含义 |
| --- | --- |
| `...` | 必填 |
| `default=` | 默认值 |
| `gt` / `ge` / `lt` / `le` | 数值范围 |
| `min_length` / `max_length` | 字符串长度限制 |
| `description` | 描述，显示在 `/docs` |

### 9.3 怎么测试 POST 接口？

GET 直接在浏览器地址栏敲就行，POST 不行。用 `/docs`：

1. 打开 http://127.0.0.1:8000/docs
2. 找到 `/register` → 点 `Try it out`
3. 编辑 `Request body` 里的 JSON → 点 `Execute`
4. 看 `Response body`

```json
{
  "username": "李四",
  "password": "123456"
}
```

用 curl 也可以：

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"李四\",\"password\":\"123456\"}"
```

### 9.4 练习

> 设计接口新增图书，图书信息包含：书名、作者、出版社、售价。要求：
> 书名：不能为空，长度 2 ~ 20；作者：长度 2 ~ 10；出版社：默认值「黑马出版社」；售价：不能为空，价格大于 0 元。

<details>
<summary>参考答案</summary>

```python
class Book(BaseModel):
    title: str = Field(..., min_length=2, max_length=20, description="书名")
    author: str = Field(..., min_length=2, max_length=10, description="作者")
    publisher: str = Field(default="黑马出版社", description="出版社")
    price: float = Field(..., gt=0, description="售价，大于0")


@app.post("/book/add")
async def add_book(book: Book):
    return book
```
</details>

---

## 10. 响应类型（对应 `代码/05`、`06`）

### 10.1 默认行为：自动 JSON

> 默认情况下，FastAPI 会自动将路径操作函数返回的 Python 对象（字典、列表、Pydantic 模型等），经由 `jsonable_encoder` 转换为 JSON 兼容格式，并包装为 `JSONResponse` 返回。

所以你 `return {"message": "hello world"}` 就够了，不需要手动序列化。

### 10.2 FastAPI 内置响应类型一览

| 响应类型 | 用途 | 示例 |
| --- | --- | --- |
| `JSONResponse` | 默认响应，返回 JSON 数据 | `return {"key": "value"}` |
| `HTMLResponse` | 返回 HTML 内容 | `return HTMLResponse(html_content)` |
| `PlainTextResponse` | 返回纯文本 | `return PlainTextResponse("text")` |
| `FileResponse` | 返回文件（下载/图片/PDF/音视频） | `return FileResponse(path)` |
| `StreamingResponse` | 流式响应 | 生成器函数返回数据 |
| `RedirectResponse` | 重定向 | `return RedirectResponse(url)` |

### 10.3 设置响应类型的两种方式

| 方式 | 场景 | 写法 |
| --- | --- | --- |
| **装饰器中指定响应类** | 固定返回类型（HTML、纯文本等） | `@app.get("/html", response_class=HTMLResponse)` |
| **返回响应对象** | 文件下载、图片、流式响应 | `return FileResponse(path)` |

### 10.4 响应 HTML 格式

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题</h1>"
```

访问 `/html`，浏览器会把它**渲染成网页**而不是显示 JSON。

### 10.5 响应文件格式

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/file")
async def get_file():
    path = "./files/1.jpeg"
    return FileResponse(path)
```

> `FileResponse` 会智能处理文件路径、媒体类型推断、范围请求和缓存头部，是服务静态文件的推荐方式。
>
> ⚠️ 路径是相对**运行命令时的工作目录**。所以要先 `cd 代码`，再 `uvicorn 06-响应类型-文件格式:app --reload`，同时确保 `代码/files/1.jpeg` 存在。

---

## 11. 自定义响应数据格式：`response_model`（对应 `代码/07-自定义响应数据格式.py`）

### 11.1 为什么需要它

讲义里有个很形象的场景：接口直接返回字典，字段写多了写少了没人管，前端拿到手「感觉哪里怪怪的」。

`response_model` 就是用来**严格定义和约束接口输出格式**的。

> `response_model` 是路径操作装饰器（如 `@app.get` 或 `@app.post`）的关键参数，它通过一个 Pydantic 模型来严格定义和约束 API 端点的输出格式。这一机制在提供自动数据验证和序列化的同时，更是保障数据安全性的第一道防线（比如可以自动过滤掉密码等敏感字段）。

### 11.2 代码

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# 需求：新闻接口 → 响应数据格式 id、title、content
class News(BaseModel):
    id: int
    title: str
    content: str


@app.get("/news/{id}", response_model=News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "这是一本好书"
    }
```

关键点：

- `response_model=News` 写在装饰器里，约束**响应**结构（请求体模型写在函数参数里，约束**输入**结构）。
- 若返回了 `News` 里没有的字段，会被自动丢弃；若缺少必填字段，会报错。
- 有了它，`/docs` 里的响应示例也会变成规范的结构。

---

## 12. 异常处理：`HTTPException`

> 对于客户端引发的错误（4xx，如资源未找到、认证失败），应使用 `fastapi.HTTPException` 来中断正常处理流程，并返回标准错误响应。

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get('/news/{id}')
async def get_news(id: int):
    id_list = [1, 2, 3, 4, 5, 6]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="当前id不存在")
    return {"id": id}
```

- `status_code`：HTTP 状态码，如 `404` 资源不存在、`401` 未认证、`403` 无权限、`400` 参数错误。
- `detail`：错误说明，会作为 JSON 返回：`{"detail": "当前id不存在"}`。
- 用 `raise` 抛出后，当前函数立即中断，后面的代码不再执行。

---

## 13. 完整运行流程速查

假设你已经有了 `main.py`：

```bash
# ① 进入项目目录
cd day01_FastAPI基础入门

# ② 激活虚拟环境
.\venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate          # macOS / Linux

# ③ 安装依赖（首次）
pip install fastapi "uvicorn[standard]"

# ④ 启动
uvicorn main:app --reload

# ⑤ 浏览器访问
#    http://127.0.0.1:8000/        查看接口返回
#    http://127.0.0.1:8000/docs    交互式文档，测 POST 接口

# ⑥ 停止
#    Ctrl + C
```

### 示例代码与运行模块名对照

| 文件 | 建议启动命令（在 `代码` 目录下） |
| --- | --- |
| `01-路由.py` | 重命名为 `route_demo.py` 后 `uvicorn route_demo:app --reload` |
| `02-路径参数.py` | 重命名为 `path_demo.py` 后 `uvicorn path_demo:app --reload` |
| `03-查询参数.py` | 重命名为 `query_demo.py` 后 `uvicorn query_demo:app --reload` |
| `04-请求体参数.py` | 重命名为 `body_demo.py` 后 `uvicorn body_demo:app --reload` |
| `05-响应类型-HTML格式.py` | 重命名后启动 |
| `06-响应类型-文件格式.py` | 必须在 `代码` 目录启动，`./files/1.jpeg` 才找得到 |
| `07-自定义响应数据格式.py` | 重命名后启动 |

> 为什么建议重命名？因为 `uvicorn` 的模块名会参与 Python 导入，中文/数字/连字符开头的文件名在部分环境下会导入失败。初学时用纯英文小写 + 下划线最稳。

---

## 14. 常见报错排查表

| 报错 / 现象 | 原因 | 解决 |
| --- | --- | --- |
| `'uvicorn' 不是内部或外部命令` | 虚拟环境没激活，或没安装 | 激活 venv；`pip install "uvicorn[standard]"`；改用 `python -m uvicorn` |
| `Could not import module "main"` | 不在 `main.py` 所在目录，或文件名/变量名写错 | 先 `cd` 到文件目录；确认 `app = FastAPI()` 变量名是 `app` |
| `ModuleNotFoundError: No module named 'fastapi'` | 装到了全局而不是 venv | 激活 venv 后重装 |
| 终端里写 `uricorn` 报错 | 拼写错误 | 正确是 `uvicorn` |
| `FileNotFoundError: ./files/1.jpeg` | 工作目录不对 | 先 `cd 代码`，再启动 |
| 访问 `127.0.0.1:8000` 打不开 | 服务没启动 / 端口被占用 | 看终端有没有 `Uvicorn running`；换端口 `uvicorn main:app --reload --port 8001` |
| 返回 `422 Unprocessable Entity` | 参数类型或约束不满足 | 看响应里的 `detail`，它会指出哪个字段不合法 |
| 改了代码没生效 | 启动时没加 `--reload` | 加上 `--reload`，或手动 `Ctrl+C` 重启 |
| 浏览器访问 POST 接口报 405 | 用浏览器地址栏发的是 GET 请求 | 用 `/docs` 或 Postman / curl 测试 |

---

## 15. 本章练习清单（自测用）

- [ ] 能独立创建项目 + 虚拟环境，并知道为什么要用虚拟环境。
- [ ] 能说出 `uvicorn main:app --reload` 三部分各是什么意思。
- [ ] 能默写一个最小 FastAPI 程序，并说清 `@app.get("/")` 的含义。
- [ ] 说出路由的定义，并解释「装饰器模式」。
- [ ] 能区分路径参数 / 查询参数 / 请求体参数的**位置、作用、适用方法**。
- [ ] 会用 `Path`、`Query`、`Field` 给参数加约束（必填、范围、长度、描述）。
- [ ] 会用 `BaseModel` 定义请求体模型，并用 `/docs` 测试 POST 接口。
- [ ] 能说出「装饰器中指定响应类」和「返回响应对象」两种设置响应类型的方式，并各举一例。
- [ ] 会用 `response_model` 约束响应格式，并解释它为什么能保障数据安全。
- [ ] 会用 `HTTPException` 返回 404 等标准错误。

全部打勾，第一章就通关了 ✅
