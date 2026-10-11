---
order: 2
tags: [MySQL, SQL, 高级查询]
prerequisites: ["[[1-Database Theory and MySQL Basics]]"]
next: "[[3-MySQL High Availability and Production Practices]]"
---

## 本章大纲

- [[#1. SQL 函数]]
- [[#2. 分组聚合]]
- [[#3. 多表查询]]
- [[#4. 子查询]]
- [[#5. 组合查询]]
- [[#6. 开窗函数]]
- [[#7. 数据操作进阶]]
- [[#8. 表操作进阶]]
- [[#9. 查询优化基础]]
- [[#10. 综合实战案例]]

## 1. SQL 函数

### 聚合函数

```sql
SELECT COUNT(*) AS total,
       SUM(amount) AS total_amount,
       AVG(amount) AS avg_amount,
       MAX(amount) AS max_amount,
       MIN(amount) AS min_amount
FROM orders;
```

- `COUNT(*)` 统计行数，`COUNT(column)` 忽略 `NULL`。
- `SUM`、`AVG` 只对数值列有意义，并忽略 `NULL`。
- `MAX`、`MIN` 可用于数字、字符串和日期类型。
- `COUNT(DISTINCT column)` 统计非空唯一值数量。
- 聚合函数会把多行压缩为一行，除非使用 `GROUP BY` 分组。

### 字符串函数

```sql
SELECT CONCAT(first_name, ' ', last_name) AS full_name,
       UPPER(username),
       SUBSTRING(phone, 1, 3),
       LENGTH(username)
FROM users;
```

- `CONCAT` 连接字符串，`SUBSTRING` 截取子串。
- `LENGTH` 返回字节长度，`CHAR_LENGTH` 返回字符长度。
- `UPPER`、`LOWER` 转换大小写。
- `TRIM`、`LTRIM`、`RTRIM` 去除空白。
- `REPLACE`、`LOCATE`、`LEFT`、`RIGHT` 用于查找和替换。

### 日期时间函数

```sql
SELECT NOW(), CURDATE(), CURTIME();
SELECT DATE(created_at), YEAR(created_at), MONTH(created_at) FROM orders;
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);
```

- `NOW` 返回当前日期时间，`CURDATE` 和 `CURTIME` 返回日期或时间。
- `DATE`、`YEAR`、`MONTH`、`DAY` 提取时间组成部分。
- `DATE_ADD`、`DATE_SUB`、`DATEDIFF`、`TIMESTAMPDIFF` 用于时间计算。
- 日期查询要明确时区、边界是否包含和索引能否命中。

### 数学与条件函数

- `ROUND`、`CEIL`、`FLOOR`、`ABS` 处理数值。
- `IF`、`IFNULL`、`COALESCE` 处理条件和非空值。
- `NULLIF(a, b)` 在两者相等时返回 `NULL`。
- `CAST`、`CONVERT` 用于数据类型转换。
- `CASE WHEN` 适合多条件分类和动态计算。

## 2. 分组聚合

```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM orders
WHERE status = 'paid'
GROUP BY customer_id
HAVING SUM(amount) > 1000
ORDER BY total DESC;
```

- `WHERE` 在分组前过滤原始行。
- `GROUP BY` 按一个或多个字段分组。
- 聚合函数在每组内部计算统计值。
- `HAVING` 在分组后过滤结果，可以使用聚合函数。
- 多字段分组会按照字段组合形成分组。
- `WITH ROLLUP` 可以生成上卷汇总行。
- 分组字段应结合业务含义和索引设计，避免高基数无序分组。

## 3. 多表查询

```sql
SELECT o.id, u.username, o.amount
FROM orders AS o
INNER JOIN users AS u ON o.user_id = u.id;
```

- `INNER JOIN` 只返回两表匹配成功的记录。
- `LEFT JOIN` 保留左表全部记录，右表无匹配时返回 `NULL`。
- `RIGHT JOIN` 保留右表全部记录。
- `CROSS JOIN` 生成笛卡尔积，必须明确使用场景。
- 自连接把同一张表当作两个逻辑表，适合层级和比较关系。
- 连接条件应使用明确字段，避免只依赖隐式条件。
- 多表连接时先确认连接键、过滤条件和结果粒度。

## 4. 子查询

```sql
SELECT username
FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE amount > 1000
);
```

- 标量子查询返回单行单列。
- 行子查询返回单行多列，表子查询返回多行多列。
- 非相关子查询独立执行一次，相关子查询依赖外层每行数据。
- `IN`、`ANY`、`ALL` 用于多值比较。
- `EXISTS` 关注子查询是否返回记录，常用于存在性判断。
- `FROM` 子查询形成派生表，必须设置别名。
- `SELECT` 子查询适合少量标量计算，过量使用会影响性能。

## 5. 组合查询

```sql
SELECT id, name FROM customers
UNION ALL
SELECT id, name FROM suppliers;
```

- `UNION` 合并结果并去重。
- `UNION ALL` 保留重复记录，通常性能更好。
- 参与组合的查询必须有相同列数和兼容的数据类型。
- `ORDER BY` 和 `LIMIT` 通常作用于最终组合结果。
- 集合操作可用于历史数据和当前数据对比、不同来源数据整合。

## 6. 开窗函数

```sql
SELECT order_id, customer_id, amount,
       ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY amount DESC
       ) AS rn
FROM orders;
```

- 窗口函数在保留明细行的同时计算分组统计。
- `OVER` 定义窗口，`PARTITION BY` 划分分区，`ORDER BY` 控制窗口顺序。
- `ROW_NUMBER` 生成连续序号，`RANK` 跳跃排名，`DENSE_RANK` 密集排名。
- `SUM OVER`、`AVG OVER` 可以计算累计和移动平均。
- `LAG`、`LEAD` 访问前后行数据，适合同比、环比和序列分析。
- 窗口框架 `ROWS` 与 `RANGE` 会影响累计范围，应明确边界。

## 7. 数据操作进阶

- `INSERT INTO ... SELECT` 把查询结果批量写入目标表。
- `INSERT ... ON DUPLICATE KEY UPDATE` 实现插入冲突更新。
- `UPDATE` 可以关联多表，但必须严格限制条件和影响行数。
- `DELETE` 应配合事务、备份或软删除策略。
- 批量操作应控制事务大小，避免长事务和锁等待。
- 生产数据变更前先执行同条件 SELECT 和 `EXPLAIN`。
- 数据导入导出可使用 `LOAD DATA`、`SELECT INTO OUTFILE` 或客户端工具。

## 8. 表操作进阶

```sql
ALTER TABLE orders ADD INDEX idx_user_created (user_id, created_at);
CREATE VIEW paid_orders AS
SELECT id, user_id, amount FROM orders WHERE status = 'paid';
```

- 表操作包括创建、修改、删除、重命名和结构复制。
- 索引可以在建表时定义，也可以通过 `ALTER TABLE` 添加。
- 视图用于封装查询、简化访问和控制字段暴露。
- 视图本身通常不存储数据，复杂视图可能影响性能。
- 表分区适合特定大表场景，但不能替代合理的索引和分库分表设计。
- 表结构变更应纳入版本化迁移脚本和回滚方案。

## 9. 查询优化基础

- 先使用 `EXPLAIN` 查看访问类型、候选索引、扫描行数和连接顺序。
- 避免 `SELECT *`，只查询必要字段。
- 在过滤、连接和排序字段上建立合适索引，但避免索引过多。
- 避免在索引列上使用函数、隐式类型转换和前置通配符。
- 小结果集优先，复杂查询可以分步拆解。
- 子查询可根据执行计划改写为连接或派生表。
- 大数据分页使用游标或延迟关联，减少大偏移扫描。

## 10. 综合实战案例

- 销售分析：按时间、地区、客户和商品维度聚合订单数据。
- 排行榜：使用窗口函数计算分组 Top N。
- 用户留存：通过日期差、分组和窗口计算留存率。
- 订单-客户-商品：使用多表连接还原业务完整数据。
- 历史与当前数据：使用 `UNION ALL` 和标识字段对比变化。
- 数据操作实战：使用事务、批量插入、条件更新和软删除完成业务变更。
- 实战查询必须同时关注结果正确性、执行计划、数据量和并发影响。
