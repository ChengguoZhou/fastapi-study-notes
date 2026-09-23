# FastAPI 学习实操笔记

> 从零开始跟课学习 FastAPI 的完整实操记录 —— **第一章 基础入门**（路由 / 参数 / 响应类型）+ **第二章 进阶**（中间件 / 依赖注入 / SQLAlchemy 异步 ORM 增删改查）。
> 每一课都是**可独立运行的单文件示例**，并配套中文实操手册，边敲边看，不依赖前面的课。

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.54-D71F00?logo=sqlalchemy&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-5.7-4479A1?logo=mysql&logoColor=white)
![uvicorn](https://img.shields.io/badge/uvicorn-0.53.0-2A2A2A)

---

## 📖 项目简介

- **面向初学者**：每个文件只讲一个知识点，代码量小、可以直接读完整篇，不用在几千行的项目里找重点。
- **可直接运行**：装好依赖即可跑。第二章 6/8 个文件、第一章 2/6 个文件末尾带 `if __name__ == "__main__"` 启动块，点一下 Run 就能起服务；其余用一行 `uvicorn 文件名:app --reload` 启动。
- **配套中文手册**：[`第一章_FastAPI入门_实操指南.md`](day01_FastAPIFoundation/第一章_FastAPI入门_实操指南.md) 与 [`第二章_实操手册.md`](day02_FastAPIAdvance/第二章_实操手册.md) 逐课讲解思路、踩坑点和常见报错，并在真实环境里实跑核对过预期返回值。
- **从接口到数据库**：第二章完成从「写一个接口」到「接口 + 异步 ORM 落库」的完整闭环，覆盖分页、模糊查询、聚合、增删改查。

---

## 🗂 目录结构

```
FastAPIDemo/
├── day01_FastAPIFoundation/                  # 第一章：FastAPI 基础入门
│   ├── 01_route.py                           # 路由：URL 与处理函数的映射
│   ├── 02_path.py                            # 路径参数 + Path 校验
│   ├── 03_query.py                           # 查询参数
│   ├── 04_response_body.py                   # 请求体参数 + Pydantic 校验
│   ├── 05_response_type.py                   # 响应类型：HTML / 文件
│   ├── 06_self_defined_response_type.py      # response_model 自定义响应格式
│   ├── file/1.jpeg                           # 05 课用到的示例图片
│   └── 第一章_FastAPI入门_实操指南.md          # 第一章实操手册
│
└── day02_FastAPIAdvance/                     # 第二章：FastAPI 进阶
    ├── 09_Middleware.py                      # 中间件：请求ID / 耗时统计 / 统一异常
    ├── 10_DependencyInjection.py             # 依赖注入 Depends
    ├── 11_ORM_CreateTable.py                 # ORM 建表
    ├── 12_ORM_ConnectTable.py                # 会话工厂与数据库依赖
    ├── 13_ORM_Select.py                      # 查询 / 条件 / 模糊 / 聚合 / 分页
    ├── 14_ORM_Insert.py                      # 新增数据
    ├── 15_ORM_Modify.py                      # 更新数据
    ├── 16_ORM_Delete.py                      # 删除数据
    ├── init_db.sql                           # 数据库初始化脚本 + 8 条演示数据
    └── 第二章_实操手册.md                     # 第二章实操手册
```

---

## 🚀 快速开始

### 1. 环境要求

| 依赖 | 版本 | 说明 |
| --- | --- | --- |
| Python | **3.12**（本项目实测） | 3.9+ 一般也可运行 |
| MySQL | 5.7 | 第二章需要；库名 `fastapi_demo` |
| FastAPI | 0.141.1 | |
| uvicorn | 0.53.0 | ASGI 服务器 |
| SQLAlchemy | 2.0.54 | 异步 ORM |
| aiomysql | 0.3.2 | MySQL 异步驱动 |
| PyMySQL | 1.2.0 | 随 aiomysql 自动安装 |

### 2. 克隆并安装依赖

```bash
git clone https://github.com/<your-name>/<repo-name>.git
cd <repo-name>

# 创建虚拟环境
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

# 安装依赖
pip install "fastapi==0.141.1" "uvicorn==0.53.0" "SQLAlchemy==2.0.54" "aiomysql==0.3.2"
```

> 也可以直接 `pip install fastapi "uvicorn[standard]" sqlalchemy aiomysql`，装最新版。

### 3. 初始化数据库（第二章需要）

```bash
mysql -uroot -p --default-character-set=utf8mb4 < day02_FastAPIAdvance/init_db.sql
```

脚本会自动建库 `fastapi_demo`、建表 `book`，并写入 8 条演示数据（覆盖不同作者、出版社和价格区间，方便验证查询、过滤、聚合、分页）。
用不到第二章的话，**可以直接跳过这一步**。

### 4. 启动并访问

进入对应章节目录，用 `uvicorn 文件名:app` 启动（文件名的 `.py` 不写）：

```bash
cd day01_FastAPIFoundation
uvicorn 01_route:app --reload --port 8000
```

打开 **http://127.0.0.1:8000/docs** 就能看到 FastAPI 自动生成的交互式文档，可以直接点 `Try it out` 测试接口。

> **文件名带数字和中文也能直接启动** —— uvicorn 使用 `importlib` 导入，不受 Python 标识符命名规则限制，**不需要改名**。
> 想用 `--reload` 热重载时，必须传字符串 `"01_route:app"`，不能传 `app` 对象，否则会报 `RuntimeError: You must pass the application as an import string to enable 'reload'`。

---

## 📚 章节导航

### 第一章 · FastAPI 基础入门

> 实操手册：[第一章_FastAPI入门_实操指南.md](day01_FastAPIFoundation/第一章_FastAPI入门_实操指南.md)

| 文件 | 知识点 | 示例接口 |
| --- | --- | --- |
| `01_route.py` | 路由：`@app.get()` 装饰器、URL 与处理函数的映射 | `GET /`、`GET /hello` |
| `02_path.py` | 路径参数 + `Path` 类型注解（`gt` / `lt` 取值范围校验） | `GET /book/{id}` |
| `03_query.py` | 查询参数 + `Query` 注解（默认值、描述） | `GET /news/news_list?skip=0&limit=10` |
| `04_response_body.py` | 请求体参数：`BaseModel` 定义结构 + `Field` 做长度校验 | `GET /register` |
| `05_response_type.py` | 响应类型：`HTMLResponse`、`FileResponse` | `GET /html`、`GET /file` |
| `06_self_defined_response_type.py` | `response_model` 用 Pydantic 模型约束响应格式 | `GET /news/{id}` |

**核心收获**：三类参数（路径 / 查询 / 请求体）的位置与适用场景、Pydantic 做数据校验、FastAPI 自动生成的 `/docs`。

### 第二章 · FastAPI 进阶

> 实操手册：[第二章_实操手册.md](day02_FastAPIAdvance/第二章_实操手册.md)

| 文件 | 知识点 | 示例接口 |
| --- | --- | --- |
| `09_Middleware.py` | 中间件洋葱模型；实战版：请求 ID 透传、访问日志与耗时统计、统一异常 JSON 响应 | `GET /ok`、`GET /slow`、`GET /boom`、`GET /notfound`、`POST /echo` |
| `10_DependencyInjection.py` | `Depends` 依赖注入，把分页参数逻辑抽出来复用 | `GET /news/news_list`、`GET /user/user_list` |
| `11_ORM_CreateTable.py` | `create_async_engine` 建引擎 + `DeclarativeBase` 定义模型 + 启动时 `create_all` 建表 | 启动时自动建表 |
| `12_ORM_ConnectTable.py` | `async_sessionmaker` 会话工厂 + `get_database` 依赖（提交 / 回滚 / 关闭） | — |
| `13_ORM_Select.py` | 查询全表、按主键查询、条件查询、模糊查询、`and_` / `or_` 组合、`func` 聚合、`offset` / `limit` 分页、排序 | `GET /book/books`、`/book/get_book/{book_id}`、`/book/search_book`、`/book/search_book/or`、`/book/search_book/author/{name}`、`/book/count`、`/book/get_page` |
| `14_ORM_Insert.py` | 新增：Pydantic DTO 接收请求体 → `db.add()` → `commit()` | `POST /book/add` |
| `15_ORM_Modify.py` | 更新：先查后改，`model_dump(exclude_unset=True)` 只更新客户端真正传过的字段 | `POST /book/update/{book_id}` |
| `16_ORM_Delete.py` | 删除：先查后删，查不到返回 404 | `DELETE /book/delete/{book_id}` |

**核心收获**：`Depends` 注入数据库会话、SQLAlchemy 2.0 异步写法（`Mapped` / `mapped_column` / `select()` / `scalar_one_or_none()`）、一个接口从「收参数」到「落库」的完整链路。

---

## 🔍 接口速查

所有示例都可以在 `/docs` 里直接测试，也可以用浏览器 / curl 访问：

```bash
# 第一章
curl http://127.0.0.1:8000/hello
curl http://127.0.0.1:8000/book/5
curl "http://127.0.0.1:8000/news/news_list?skip=0&limit=10"

# 第二章（需要先初始化数据库）
curl "http://127.0.0.1:8000/book/get_page?page=1&page_size=3"
curl "http://127.0.0.1:8000/book/search_book?bookname=Python&min_price=50&order_by=price&desc=true"
curl http://127.0.0.1:8000/book/count
```

> ⚠️ **同一时间只能跑一个文件**，否则会报 `[Errno 10048] 端口已被占用`。
> 换课的时候先停掉上一个服务，或者给每个文件换端口 —— 项目里 `15_ORM_Modify.py` 用 8007、`16_ORM_Delete.py` 用 8008，就是这么处理的。

---

## 🧰 技术栈

| 分类 | 技术 |
| --- | --- |
| 语言 | Python 3.12 |
| Web 框架 | FastAPI |
| ASGI 服务器 | uvicorn |
| 数据校验 | Pydantic 2.x |
| ORM | SQLAlchemy 2.0（异步） |
| 数据库 | MySQL 5.7 |
| 异步驱动 | aiomysql / PyMySQL |
| 开发工具 | PyCharm |

---

## ❓ 常见问题

| 问题 | 原因与解决 |
| --- | --- |
| `[Errno 10048] 端口已被占用` | 上一个服务没停。点红色方块停掉，或换端口 `--port 8001` |
| `RuntimeError: ... import string to enable 'reload'` | 热重载必须传字符串 `"03_query:app"`，不能传 `app` 对象 |
| `Access denied for user 'root'` | 连接串里的账号密码和本机不一致，改 `ASYNC_DB_URL` |
| `Unknown database 'fastapi_demo'` | 没初始化数据库，执行 `init_db.sql` |
| `Invalid args for response field!` | `response_model=` 后面跟的类**必须继承 `BaseModel`**，普通类不合法 |
| 浏览器 / `/docs` 看到的返回顺序和课件不一样 | 以实测为准。例如中间件的执行顺序与 Starlette 版本有关，可用 `print([m.kwargs["dispatch"].__name__ for m in app.user_middleware])` 确认 |
| 中文乱码 | 连接串带上 `?charset=utf8mb4`，建库时也用 `utf8mb4` |

更多报错排查见两份实操手册的「常见报错」章节。

---

## 📌 说明

- **数据库连接串**：示例里写的是本地演示用的 `mysql+aiomysql://root:root@localhost:3306/fastapi_demo?charset=utf8mb4`，**请改成你自己的账号密码**。正式项目建议改成读环境变量，不要把凭据写死在代码里。
- 本仓库是**个人学习笔记**，代码以「看得懂、跑得起来」为第一目标，刻意保留了重复的骨架代码，没有做工程化封装。生产项目请参考 `routers/` + `models/` + `crud/` + `schemas/` 的分层写法。
- 手册中的结论均在 Python 3.12.13 + FastAPI 0.141.1 + MySQL 5.7.32 环境下实跑核对；其中若与课件表述不一致，**以手册为准**（手册里标注了差异原因）。
- 学习过程中如果发现课件与实测不符，欢迎提 Issue，这类记录对后来的人最有用。
