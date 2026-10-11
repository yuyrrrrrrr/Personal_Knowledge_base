---
order: 2
tags: [Linux, Shell, 脚本]
prerequisites: ["[[1-System Management]]"]
next: "[[3-Administration of Networks]]"
---

## 本章大纲

- [[#1. Shell 基础]]
- [[#2. 变量与数组]]
- [[#3. 条件判断]]
- [[#4. 循环与流程控制]]
- [[#5. 函数与参数]]
- [[#6. 管道、重定向与文本处理]]
- [[#7. 运维自动化脚本]]
- [[#8. 定时任务 Cron]]

## 1. Shell 基础

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Hello, Linux"
```

- Shell 是用户与操作系统内核之间的命令解释器。
- 常见 Shell 包括 `bash`、`zsh`、`fish`，服务器脚本通常优先使用 `bash`。
- Shebang 指定脚本解释器，例如 `#!/usr/bin/env bash`。
- 执行脚本前需要添加执行权限：`chmod +x script.sh`。
- `set -e` 在命令失败时退出，`set -u` 禁止使用未定义变量，`set -o pipefail` 捕获管道错误。
- 命令、选项和参数之间使用空格分隔，变量展开时通常加双引号。

## 2. 变量与数组

### 变量

```bash
name="Alice"
count=3
echo "${name} ${count}"
```

- Shell 变量赋值时等号两边不能有空格。
- 推荐使用 `"${变量名}"`，避免空格和特殊字符导致参数拆词。
- `export VAR=value` 把变量导出为子进程可用的环境变量。
- 命令替换使用 `$(command)`，算术运算可使用 `$((...))`。
- 变量默认都是字符串，参与算术时由 Shell 进行解释。

### 数组

```bash
hosts=("web1" "web2" "db1")
echo "${hosts[0]}"
echo "${hosts[@]}"
echo "${#hosts[@]}"
```

- Bash 数组通过 `名字=(元素1 元素2)` 创建。
- `${array[index]}` 读取单个元素，`${array[@]}` 展开所有元素。
- `${#array[@]}` 获取元素数量。
- 遍历数组时使用 `"${array[@]}"`，保留每个元素的边界。
- 关联数组使用 `declare -A map`，通过字符串键访问值。

## 3. 条件判断

```bash
if [[ -f "$file" && -r "$file" ]]; then
    echo "文件存在且可读"
elif [[ -d "$path" ]]; then
    echo "这是目录"
else
    echo "条件不成立"
fi
```

- `if`、`elif`、`else` 按顺序判断条件。
- `[[ ... ]]` 是 Bash 的条件表达式，支持字符串、文件和逻辑判断。
- 字符串比较常用 `==`、`!=`，整数比较常用 `-eq`、`-ne`、`-lt`、`-gt`。
- 文件判断常用 `-e`、`-f`、`-d`、`-r`、`-w`、`-x`。
- `&&` 表示前一个命令成功后执行，`||` 表示失败后执行。
- `case` 适合匹配多个固定分支。

```bash
case "$1" in
    start) echo "启动" ;;
    stop) echo "停止" ;;
    *) echo "未知参数" ;;
esac
```

## 4. 循环与流程控制

```bash
for host in "${hosts[@]}"; do
    echo "检查 ${host}"
done

count=0
while (( count < 3 )); do
    ((count++))
done
```

- `for` 适合遍历列表、文件、命令输出和固定范围。
- `while` 在条件为真时反复执行，`until` 在条件为假时反复执行。
- `break` 结束整个循环，`continue` 跳过本次迭代。
- `read -r line` 可逐行读取文件或标准输入。
- 循环变量和命令展开应使用引号，避免文件名中包含空格时出错。
- 脚本中要处理空列表、空文件和命令执行失败等边界情况。

## 5. 函数与参数

```bash
check_service() {
    local service="$1"
    systemctl is-active --quiet "$service"
}

check_service nginx || echo "nginx 未运行"
```

- 函数通过 `函数名() { ... }` 定义，使用 `函数名 参数` 调用。
- `$1`、`$2` 表示位置参数，`$#` 表示参数数量，`$@` 表示全部参数。
- `local` 声明函数内部变量，避免污染全局作用域。
- `return` 返回整数状态码，业务数据通常通过标准输出返回。
- `$?` 保存上一条命令的退出状态，`0` 通常表示成功。
- 函数应保持单一职责，并检查必要参数和命令是否存在。

## 6. 管道、重定向与文本处理

```bash
command > output.log 2>&1
cat access.log | grep "500" | wc -l
```

- `>` 覆盖标准输出，`>>` 追加标准输出，`2>` 重定向标准错误。
- `2>&1` 把标准错误合并到标准输出。
- `|` 把前一个命令的标准输出传给下一个命令。
- `grep`、`sed`、`awk`、`cut`、`sort`、`uniq`、`wc` 常用于日志处理。
- `xargs` 可以把标准输入转换为命令参数。
- 处理生产数据前应先小范围验证，避免误删、误改或覆盖文件。

## 7. 运维自动化脚本

### 系统监控脚本

- 检查 CPU、内存、磁盘和进程状态。
- 当阈值超限时输出告警、写日志或调用通知接口。
- 避免在高频脚本中执行重型命令。

### 日志分析脚本

- 统计错误数量、访问来源、响应码和高频关键字。
- 使用 `grep`、`awk`、`sed`、`sort`、`uniq` 组合处理文本。
- 对日志轮转、压缩文件和跨日边界进行考虑。

### 自动化部署脚本

- 先检查环境和参数，再执行备份、上传、解压、切换和验证。
- 每个关键步骤都检查退出码，失败时停止并输出明确日志。
- 生产部署应支持幂等、回滚和变更记录。

## 8. 定时任务 Cron

```bash
crontab -e

# 每天 02:30 执行备份
30 2 * * * /opt/scripts/backup.sh >> /var/log/backup.log 2>&1
```

- Cron 五个时间字段依次表示分钟、小时、日、月、星期。
- `crontab -l` 查看当前用户任务，`crontab -e` 编辑任务。
- 脚本应使用绝对路径，并明确设置 `PATH`、工作目录和环境变量。
- 标准输出和错误输出应重定向到日志，便于排查失败。
- 使用锁文件或 `flock` 防止任务重复执行。
- 定时任务完成后应验证结果，而不是只确认命令已执行。
