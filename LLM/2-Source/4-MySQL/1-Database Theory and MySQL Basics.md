---
order: 1
tags: [MySQL, SQL, 数据库基础]
next: "[[2-SQL Practical Application and Advanced Topics]]"
---

## 本章大纲

- [[#1. 数据库基础]]
- [[#2. 关系模型与数据库设计]]
- [[#3. SQL 语言分类]]
- [[#4. MySQL 安装与连接]]
- [[#5. 数据库与数据表操作]]
- [[#6. 数据类型、约束与存储引擎]]
- [[#7. 基础查询]]
- [[#8. 条件查询]]
- [[#9. 排序、分页与去重]]
- [[#10. 数据增删改]]

## 1. 数据库基础

- 数据是原始记录，信息是经过组织和解释后具有意义的数据。
- 数据库用于持久化组织和管理数据，核心目标是可靠存储、高效查询和并发访问。
- `DBMS` 是数据库管理系统，负责数据的定义、存储、查询、权限、事务和恢复。
- 关系型数据库使用二维表组织数据，常见产品包括 `MySQL`、`PostgreSQL`、`Oracle`、`SQL Server`。
- 非关系型数据库包括键值、文档、列族和图形数据库，适合特定数据模型和扩展场景。
- MySQL 是开源关系型数据库，常见于 Web 后端、数据分析和企业业务系统。

记忆术语：

- 表（`Table`）：由行和列组成的数据集合。
- 字段或列（`Column`）：描述数据的一个属性。
- 记录或行（`Row`）：一条完整数据。
- 主键（`Primary Key`）：唯一标识一条记录。
- 外键（`Foreign Key`）：建立表与表之间的引用关系。
- 索引（`Index`）：加速数据查找，但会增加写入和维护成本。
- 视图（`View`）：基于查询定义的虚拟表。
- 事务（`Transaction`）：一组要么全部成功、要么全部失败的操作。

## 2. 关系模型与数据库设计

### 关系与表

- 关系可以理解为一个二维表，行表示实体记录，列表示属性。
- 一个数据库可以包含多张表，表之间通过主键和外键建立关系。
- 主键不能重复且不能为 `NULL`，业务主键应保持稳定。
- 外键用于保证引用完整性，并维护一对一、一对多和多对多关系。

### 表关联关系

- 一对一：两个表各自保存一条对应记录，例如用户和用户档案。
- 一对多：一张表的一条记录对应另一张表的多条记录，例如用户和订单。
- 多对多：通常通过中间表实现，例如学生和课程。
- `E-R` 图用于表达实体、属性和实体之间的关系。

### 三大范式

- 第一范式 `1NF`：字段保持原子性，不在一个字段中保存多个不可拆分值。
- 第二范式 `2NF`：满足 `1NF`，且非主键字段完全依赖主键。
- 第三范式 `3NF`：满足 `2NF`，且非主键字段不传递依赖其他非主键字段。
- 实际项目需要在范式化和查询性能之间权衡，允许适度反范式。

### 数据完整性

- 实体完整性通过主键保证记录唯一。
- 参照完整性通过外键保证关联记录有效。
- 域完整性通过数据类型、非空、默认值和检查约束限制字段取值。
- 用户定义完整性通过业务规则和触发器等方式补充。

## 3. SQL 语言分类

| 分类 | 作用 | 常见语句 |
|---|---|---|
| `DDL` | 定义和修改数据库对象 | `CREATE`、`ALTER`、`DROP`、`TRUNCATE` |
| `DML` | 操作表中的数据 | `INSERT`、`UPDATE`、`DELETE` |
| `DQL` | 查询数据 | `SELECT` |
| `DCL` | 控制权限 | `GRANT`、`REVOKE` |
| `TCL` | 控制事务 | `COMMIT`、`ROLLBACK`、`SAVEPOINT` |

- SQL 关键字通常不区分大小写，但关键字使用大写、名称使用小写更易读。
- 字符串字面量通常使用单引号。
- 注释可以使用 `-- 注释`、`# 注释` 或 `/* 注释 */`。
- SQL 编写应保持缩进、换行和命名一致。

## 4. MySQL 安装与连接

### 安装与初始化

- Linux 上可通过发行版仓库、官方仓库或二进制包安装 MySQL。
- 安装后需要初始化数据目录、启动服务并设置认证方式。
- 生产环境应明确数据目录、端口、字符集、时区和日志路径。
- 首次安装后应立即设置 `root` 密码并删除匿名账号和测试库。

### 连接数据库

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
mysql -u root -p --database=learn_sql
```

```sql
SELECT VERSION();
SELECT CURRENT_USER();
SHOW DATABASES;
```

- 图形化客户端可使用 `MySQL Workbench`、`Navicat`、`DBeaver`。
- 命令行适合自动化、远程管理和问题排查。
- 连接失败时应检查服务状态、端口、网络、认证插件、用户主机范围和防火墙。

## 5. 数据库与数据表操作

### 数据库操作

```sql
CREATE DATABASE learn_sql CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE learn_sql;
SHOW DATABASES;
DROP DATABASE learn_sql;
```

- `CREATE DATABASE` 创建数据库，`USE` 选择当前数据库。
- `SHOW DATABASES` 查看数据库列表，`DROP DATABASE` 删除数据库及其对象。
- 生产环境删除数据库前必须确认备份和影响范围。

### 数据表操作

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    age INT CHECK (age >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN email VARCHAR(100);
DESC users;
DROP TABLE users;
```

- `CREATE TABLE` 创建表，`ALTER TABLE` 修改表结构，`DROP TABLE` 删除表。
- `DESC` 或 `SHOW CREATE TABLE` 查看表结构。
- `TRUNCATE TABLE` 快速清空数据，通常不可回滚。
- 修改大表结构时要评估锁表时间、磁盘空间和业务影响。

## 6. 数据类型、约束与存储引擎

### 常用数据类型

- 整数类型：`TINYINT`、`INT`、`BIGINT`。
- 小数类型：`DECIMAL` 适合金额，`FLOAT` 和 `DOUBLE` 存在精度风险。
- 字符串类型：`CHAR` 定长、`VARCHAR` 变长、`TEXT` 大文本。
- 日期时间类型：`DATE`、`TIME`、`DATETIME`、`TIMESTAMP`。
- 枚举与集合：`ENUM`、`SET` 仅适合取值稳定的场景。
- `NULL` 表示未知值，判断必须使用 `IS NULL` 或 `IS NOT NULL`。

### 常用约束

- `PRIMARY KEY`：主键约束。
- `FOREIGN KEY`：外键约束。
- `UNIQUE`：唯一性约束。
- `NOT NULL`：非空约束。
- `DEFAULT`：默认值。
- `CHECK`：取值检查约束。

### 存储引擎

- `InnoDB` 是默认存储引擎，支持事务、行级锁、外键和崩溃恢复。
- `MyISAM` 不支持事务，主要适合只读或历史兼容场景。
- 新项目通常优先选择 `InnoDB`。

## 7. 基础查询

```sql
SELECT * FROM users;
SELECT id, username FROM users;
SELECT username AS user_name FROM users;
SELECT price, quantity, price * quantity AS total_amount FROM order_items;
```

- `SELECT` 指定返回列，`FROM` 指定数据来源。
- `SELECT *` 适合临时查看，正式代码应明确字段。
- `AS` 为列或表达式设置别名。
- 计算列不会自动存储，除非使用生成列。
- 查询结果顺序在没有 `ORDER BY` 时不保证稳定。

## 8. 条件查询

```sql
SELECT * FROM users
WHERE age >= 18
  AND (city = '上海' OR city = '北京');

SELECT * FROM users WHERE username LIKE 'A%';
SELECT * FROM users WHERE age IN (18, 20, 25);
SELECT * FROM users WHERE age BETWEEN 18 AND 30;
SELECT * FROM users WHERE email IS NULL;
```

- `WHERE` 在分组前过滤原始行。
- `AND`、`OR`、`NOT` 组合多个条件，括号用于明确优先级。
- 比较运算符包括 `=`、`<>`、`!=`、`>`、`<`、`>=`、`<=`。
- `LIKE` 配合 `%` 和 `_` 实现模式匹配。
- `IN` 判断是否属于集合，`BETWEEN` 判断闭区间。
- `CASE WHEN` 可以实现条件分支和结果分类。
- 对 `NULL` 使用 `= NULL` 不会成立，必须使用 `IS NULL`。

## 9. 排序、分页与去重

```sql
SELECT id, username, age
FROM users
ORDER BY age DESC, id ASC
LIMIT 10 OFFSET 20;

SELECT DISTINCT city FROM users;
```

- `ORDER BY` 控制结果顺序，`ASC` 为升序，`DESC` 为降序。
- 多列排序按列顺序依次比较。
- 未显式指定时，`NULL` 的排序位置由数据库实现决定。
- `LIMIT` 限制返回数量，`OFFSET` 跳过前若干行。
- 大偏移分页性能会下降，可使用基于游标的分页。
- `DISTINCT` 对结果行去重，会影响性能并需要明确去重范围。

## 10. 数据增删改

### 插入数据

```sql
INSERT INTO users (username, age) VALUES ('alice', 18);
INSERT INTO users (username, age) VALUES ('bob', 20), ('carol', 22);
```

- 明确列出插入字段，避免表结构变化导致错误。
- 批量插入通常比逐条插入效率更高。
- `INSERT INTO ... SELECT` 可以把查询结果写入另一张表。

### 更新数据

```sql
UPDATE users SET age = age + 1 WHERE id = 1;
```

- `UPDATE` 必须配合明确的 `WHERE`，否则会更新整张表。
- 更新前先执行同条件的 `SELECT` 确认影响范围。
- 多表更新和关联更新需要理解锁范围与执行计划。

### 删除数据

```sql
DELETE FROM users WHERE id = 1;
```

- `DELETE` 删除满足条件的行，可以配合事务回滚。
- `TRUNCATE TABLE` 清空整表，速度快但通常不能回滚。
- 生产环境删除数据前应备份，并优先使用软删除或归档策略。
