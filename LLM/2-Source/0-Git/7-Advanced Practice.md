---
order: 7
tags: [Git, 原理, 故障排查]
prerequisites: ["[[6-Tools and Platforms]]"]
next: "[[8-Comprehensive Project Practice]]"
---

## 本章大纲

- [[#1. Git 内部原理]]
- [[#2. 引用系统与传输协议]]
- [[#3. 自定义配置与别名]]
- [[#4. Git Hooks]]
- [[#5. 常见故障排除]]
- [[#6. 性能、安全与最佳实践]]

## 1. Git 内部原理

```bash
git cat-file -t HEAD
git cat-file -p HEAD
git rev-parse HEAD^{tree}
```

- Git 是内容寻址的对象数据库，对象通过哈希标识。
- blob 保存文件内容，tree 保存目录结构，commit 保存历史关系。
- commit 通过父提交形成有向无环图。
- 分支和 HEAD 保存在引用文件中，最终指向提交对象。
- 对象可以打包为 packfile，减少存储和网络传输成本。
- 理解对象模型有助于分析 detached HEAD、悬空提交和历史恢复问题。

## 2. 引用系统与传输协议

- 引用通常位于 `.git/refs/`，打包引用位于 `packed-refs`。
- `HEAD` 可以指向分支，也可以直接指向提交形成 detached HEAD。
- 远程引用、标签和本地分支分别属于不同命名空间。
- Git 支持本地、SSH、HTTP(S) 等传输方式。
- fetch 协商需要传输的对象，push 上传本地新增对象并更新远程引用。
- 理解引用更新规则有助于排查远程分支不同步和标签丢失问题。

## 3. 自定义配置与别名

```bash
git config --global alias.st "status --short"
git config --global alias.lg "log --oneline --graph --decorate"
git config --global core.autocrlf input
git config --global diff.tool vimdiff
```

- 别名可以缩短常用命令，但不应隐藏危险操作。
- 换行符配置要结合操作系统和团队规范。
- 自定义 diff、merge 和编辑器可以提升冲突处理效率。
- `.gitattributes` 可以按文件类型定义换行符、合并策略和文本属性。
- 仓库级配置适合项目特定规则，用户级配置适合个人偏好。
- 配置变更应记录原因，避免不同环境行为不一致。

## 4. Git Hooks

- Hook 是在特定 Git 事件前后自动执行的脚本。
- 常见 Hook 包括 `pre-commit`、`commit-msg`、`pre-push`、`post-merge`。
- Hook 可以运行格式化、Lint、测试、提交信息检查和敏感信息扫描。
- 本地 `.git/hooks` 不会被版本控制，团队通常使用工具管理共享 Hook。
- Hook 应保持快速、明确并允许必要的绕过机制。
- 关键质量门禁应在服务端或 CI 中再次执行，不能只依赖本地 Hook。

## 5. 常见故障排除

- 推送被拒绝：检查远程新提交、分支跟踪和权限。
- 合并冲突：确认冲突范围、业务语义和最终文件内容。
- Detached HEAD：确认当前提交，必要时创建新分支保存工作。
- 提交错误分支：使用 cherry-pick、reset 或交互式变基调整。
- 误删分支：使用 `reflog` 查找引用并创建恢复分支。
- 仓库损坏：使用 `git fsck`、备份和克隆副本谨慎恢复。
- 大文件导致仓库膨胀：清理历史和迁移到 Git LFS，操作前必须备份。

## 6. 性能、安全与最佳实践

- 使用浅克隆、部分克隆和稀疏检出减少大型仓库下载成本。
- 避免长期保存大二进制文件，必要时应使用 Git LFS。
- `git gc` 可以维护对象和打包，但不应在无备份的异常仓库上直接操作。
- 定期审查 SSH 密钥、令牌、签名和仓库权限。
- 使用提交签名和分支保护防止伪造提交和绕过审查。
- 对历史中的敏感信息泄露应立即轮换凭据，而不是只删除当前文件。
- 团队应统一提交规范、分支策略、审查规则和 CI 质量门禁。
