---
order: 6
tags: [Git, 工具, 平台]
prerequisites: ["[[5-Advanced Features]]"]
next: "[[7-Advanced Practice]]"
---

## 本章大纲

- [[#1. Git 图形界面工具]]
- [[#2. GitHub 基础功能]]
- [[#3. Issues 与项目管理]]
- [[#4. Pull Request 与 GitHub Actions]]
- [[#5. 其他托管平台]]
- [[#6. 平台迁移与认证管理]]

## 1. Git 图形界面工具

- GUI 工具可以降低查看差异、暂存和提交的操作门槛。
- SourceTree、GitHub Desktop、GitKraken、IDE 内置 Git 都是常见选择。
- 图形界面适合查看历史和解决冲突，命令行更适合自动化和精确操作。
- 不应只依赖按钮记忆，仍需理解 Git 的状态和对象模型。
- 使用 GUI 前应确认它不会自动执行不透明的强制操作。
- 命令行与 GUI 可以混合使用，但必须保持对仓库状态的一致理解。

## 2. GitHub 基础功能

- Repository 用于保存代码、文档、Issue、Release 和自动化配置。
- Star、Fork、Watch 分别用于关注、复制和维护通知。
- README 是项目入口，应说明用途、安装、运行和贡献方式。
- 仓库设置包括可见性、分支保护、权限、Webhook 和 Actions。
- 提交者身份应通过 SSH 密钥、令牌或组织 SSO 安全认证。
- 公开仓库不应提交密钥、用户数据或内部配置。

## 3. Issues 与项目管理

- Issue 适合记录缺陷、需求、讨论和待办事项。
- Issue 应包含背景、复现步骤、预期结果、实际结果和环境信息。
- Labels、Milestones、Assignees 和 Projects 用于组织和跟踪工作。
- Pull Request 可以通过关键词关联 Issue，并在合并时关闭。
- 模板、自动标签和表单可以提升协作质量。
- 任务状态应与实际开发进度同步，避免长期失效的看板。

## 4. Pull Request 与 GitHub Actions

```yaml
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "run tests"
```

- Pull Request 是代码审查、讨论和合并的核心流程。
- Actions 通过工作流自动执行测试、构建、扫描和发布。
- Workflow、Job、Step、Action 是 GitHub Actions 的核心概念。
- Secrets 用于保存令牌和密码，不应直接写入日志或 YAML。
- 工作流权限应遵循最小权限原则，第三方 Action 应固定可信版本。
- CI 失败应视为质量信号，不应习惯性忽略后再合并。

## 5. 其他托管平台

- GitLab：提供仓库、CI/CD、Issue、代码审查和自托管能力。
- Bitbucket：常与 Atlassian 工具链协作，支持 Pull Request 和流水线。
- Gitee：国内常用代码托管平台，提供仓库、Issue 和 PR 等功能。
- 不同平台的术语略有差异，但核心 Git 对象和协作模型一致。
- 选择平台时应考虑访问速度、权限、CI、合规和团队习惯。
- 不应把平台专有功能耦合到不可迁移的核心流程中。

## 6. 平台迁移与认证管理

- 迁移仓库前应确认提交历史、分支、标签、Issue、PR 和 CI 配置。
- 远程地址迁移可以通过 `git remote set-url` 完成。
- 迁移后应重新配置权限、Webhook、Secrets、分支保护和部署密钥。
- SSH 密钥应使用强口令并定期轮换，私钥不能上传到平台。
- 访问令牌应限制权限和有效期，发现泄露立即撤销。
- 多平台协作时要明确主仓库、镜像仓库和同步方向。
