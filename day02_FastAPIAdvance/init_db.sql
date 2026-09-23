-- ============================================================
-- FastAPI 第二章 实操：数据库初始化脚本
-- 数据库：fastapi_demo    账号：root / root
-- 用法（cmd 或 PowerShell 均可）：
--   "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" -uroot -proot --default-character-set=utf8mb4 < init_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS fastapi_demo
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE fastapi_demo;

-- ------------------------------------------------------------
-- 书籍表 book：与 11-ORM-建表.py 中的 Book 模型一一对应
--   Base  提供：create_time、update_time
--   Book  提供：id、bookname、author、price、publisher
-- 说明：SQLAlchemy 的 create_all 会先检查表是否存在，
--       表已存在则直接跳过，所以这里先建好不影响第 11 课演示。
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book (
    id          INT          NOT NULL AUTO_INCREMENT COMMENT '书籍id',
    bookname    VARCHAR(255) NOT NULL COMMENT '书名',
    author      VARCHAR(255) NOT NULL COMMENT '作者',
    price       FLOAT        NOT NULL COMMENT '价格',
    publisher   VARCHAR(255) NOT NULL COMMENT '出版社',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    PRIMARY KEY (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '书籍表';

-- ------------------------------------------------------------
-- 演示数据：8 条，覆盖不同作者 / 出版社 / 价格区间
-- 作用：第 13~17 课的查询、过滤、模糊、聚合、分页都能看到结果
--       （第 13 课的 db.get(Book, 5) 需要 id=5 存在）
-- ------------------------------------------------------------
TRUNCATE TABLE book;

INSERT INTO book (id, bookname, author, price, publisher) VALUES
(1, 'Python编程从入门到实践', 'Eric Matthes', 89.00,  '人民邮电出版社'),
(2, '流畅的Python',           'Luciano Ramalho', 139.00, '人民邮电出版社'),
(3, 'FastAPI Web开发',        'Bill Lubanovic', 99.00,  '机械工业出版社'),
(4, 'SQLAlchemy实战',         'Jason Myers',   79.00,  '电子工业出版社'),
(5, '深入理解计算机系统',      'Randal Bryant', 128.00, '机械工业出版社'),
(6, 'MySQL必知必会',          'Ben Forta',     45.00,  '人民邮电出版社'),
(7, 'Python异步编程',         'Caleb Hattingh', 69.00, '电子工业出版社'),
(8, '代码整洁之道',           'Robert Martin', 59.00,  '清华大学出版社');

-- 结果确认
SELECT COUNT(*) AS 书籍总数, MAX(price) AS 最高价, MIN(price) AS 最低价, AVG(price) AS 平均价 FROM book;
SELECT id, bookname, author, price, publisher FROM book ORDER BY id;
