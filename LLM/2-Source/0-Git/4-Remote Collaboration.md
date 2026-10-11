---
order: 4
tags: [Git, 远程协作]
prerequisites: ["[[3-Branch Management]]"]
next: "[[5-Advanced Features]]"
---

## 本章大纲

- [[#1. 远程仓库基础]]
- [[#2. fetch、pull 与 push]]
- [[#3. 跟踪分支与远程分支]]
- [[#4. 推送冲突与强制推送]]
- [[#5. 标签与版本发布]]
- [[#6. 协作工作流]]
- [[#7. Pull Request 与代码审查]]

## 1. 远程仓库基础

```bash
git remote -v
git remote add origin https://example.com/team/project.git
git remote set-url origin git@example.com:team/project.git
git remote remove origin
```

- 远程仓库是协作和备份的共享位置，常见平台包括 GitHub、GitLab、Gitee。
- `origin` 是克隆后默认远程名称，但名称可以自定义。
- HTTPS 适合简单访问，SSH 更适合长期开发和自动化。
- 远程仓库地址变更后要同步更新本机配置。
- 私钥、访问令牌和密码不能提交到仓库或写死在脚本中。

## 2. fetch、pull 与 push

```bash
git fetch origin
git pull --rebase origin main
git push -u origin feature/login
```

- `fetch` 只下载远程对象和引用，不改动当前工作区。
- `pull` 通常等价于 `fetch` 加 `merge` 或 `rebase`。
- `push` 把本地提交上传到远程分支。
- `push -u` 建立本地分支与远程分支的跟踪关系。
- 合并策略应结合团队规范，避免在不了解差异时直接拉取。
- 推送前应检查本地提交、分支和远程状态。

## 3. 跟踪分支与远程分支

```bash
git branch -vv
git switch -c feature/login origin/feature/login
git branch --set-upstream-to=origin/main main
```

- 远程分支是远程仓库状态在本地的只读引用。
- 跟踪分支记录本地分支对应的默认上游。
- `git status` 会提示当前分支与上游的领先或落后情况。
- 删除远程分支后，可执行 `git fetch --prune` 清理失效的远程引用。
- 不应直接修改 `origin/main`，而应先创建本地工作分支。

## 4. 推送冲突与强制推送

- 推送被拒绝通常表示远程已有本地没有的提交。
- 应先拉取或变基、解决冲突、运行测试，再重新推送。
- `--force` 会覆盖远程历史，可能破坏协作者的工作。
- `--force-with-lease` 会在远程状态与预期不一致时拒绝覆盖，风险更低。
- 共享分支应优先通过 revert 或追加提交修复，而不是重写历史。
- 修改远程历史前必须通知团队并确认没有其他人依赖。

## 5. 标签与版本发布

```bash
git tag -a v1.0.0 -m "release v1.0.0"
git show v1.0.0
git push origin v1.0.0
git push origin --tags
```

- 轻量标签只是指向提交的引用，附注标签包含标签对象、作者和说明。
- 版本发布通常使用附注标签，例如 `v1.0.0`。
- 标签默认不会随普通 `push` 自动上传，需要单独推送。
- 删除远程标签会影响其他协作者，必须谨慎操作。
- 发布流程应关联版本号、变更日志、构建产物和回滚方案。

## 6. 协作工作流

- Fork 工作流：开发者复制公共仓库，在自己的仓库开发并提交 Pull Request。
- Feature Branch 工作流：每个功能或修复使用独立分支，经审查后合并。
- Gitflow：适合有明确发布节奏的团队，分支角色和 release 流程较完整。
- Trunk-Based：频繁集成到主干，依赖自动化测试和短生命周期分支。
- 工作流应明确分支来源、命名、审查、合并和发布规则。
- 分支越短，合并冲突和集成风险通常越低。

## 7. Pull Request 与代码审查

- Pull Request 用于提议合并代码、讨论差异和记录审查结论。
- PR 应保持范围清晰，避免同时包含多个无关功能。
- 描述应包含目标、实现方式、验证结果和风险。
- 审查关注正确性、可读性、测试、安全、性能和向后兼容。
- 评论应针对代码和行为，避免对个人进行评价。
- 合并前应确认 CI、审查、冲突、测试和部署条件都已满足。
