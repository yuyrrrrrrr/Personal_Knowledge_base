---
order: 1
tags: [Git, 版本控制, 基础]
next: "[[2-Core Operations]]"
---

## 本章大纲

- [[#1. 版本控制与 Git]]
- [[#2. 集中式与分布式版本控制]]
- [[#3. Git 安装与环境配置]]
- [[#4. 仓库、工作区与暂存区]]
- [[#5. Git 对象模型]]
- [[#6. 文件生命周期]]
- [[#7. 第一次提交流程]]

## 1. 版本控制与 Git

- 版本控制用于记录文件变化、追踪历史、比较版本和恢复旧状态。
- 版本控制系统可以支持多人协作、分支开发、代码审查和发布管理。
- Git 是分布式版本控制系统，强调本地完整历史、快速分支和离线操作。
- Git 保存的是内容快照和提交历史，不是简单复制整个目录。
- Git 适合源代码，也适合文档、配置和其他需要版本追踪的文本文件。

## 2. 集中式与分布式版本控制

- 集中式版本控制依赖中央服务器，客户端通常只保存工作副本和有限历史。
- 集中式系统在网络断开后，很多版本操作无法进行。
- 分布式版本控制会在本地保存完整仓库历史和对象。
- 分布式系统仍可配置中央远程仓库，但本地提交不依赖网络。
- Git 的分支和合并成本较低，适合频繁开发和协作。

## 3. Git 安装与环境配置

### 安装

- Windows 可使用官方安装包或 `winget install Git.Git`。
- macOS 可使用 `brew install git` 或安装 Xcode Command Line Tools。
- Linux 可使用 `apt install git`、`dnf install git` 等包管理器命令。
- 安装后使用 `git --version` 验证。

### 配置

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.editor "vim"
```

- `--system`、`--global`、`--local` 分别表示系统级、用户级和仓库级配置。
- 配置会在不同层级之间覆盖，优先级通常为仓库、用户、系统。
- `git config --list --show-origin` 可以查看配置来源。
- 用户名和邮箱会写入提交记录，提交前必须确认正确。
- 编辑器、换行符、颜色和别名等配置可以按环境调整。

## 4. 仓库、工作区与暂存区

```text
工作区 -> git add -> 暂存区 -> git commit -> 本地仓库
```

- 工作区是当前可见并可编辑的文件目录。
- 暂存区保存准备进入下一次提交的变更。
- 本地仓库保存提交对象、分支引用和版本历史。
- `HEAD` 通常指向当前分支的最新提交。
- `git status` 显示工作区和暂存区相对于 HEAD 的状态。
- 暂存区允许把一次大改动拆成多个逻辑清晰的提交。

## 5. Git 对象模型

- `blob`：保存文件内容。
- `tree`：保存目录结构和文件、子目录引用。
- `commit`：保存一次提交的树、父提交、作者和提交信息。
- `tag`：保存指向特定对象的命名引用，通常指向提交。
- `ref`：保存分支、标签和 HEAD 等引用。
- Git 对象通过 SHA-1 或 SHA-256 哈希标识，内容相同可以复用对象。
- `git cat-file`、`git hash-object` 可用于查看和创建对象。

## 6. 文件生命周期

- 未跟踪：文件存在，但从未被 Git 管理。
- 已修改：已跟踪文件内容发生变化，尚未暂存。
- 已暂存：变更已经进入暂存区，准备提交。
- 已提交：变更已写入本地仓库历史。
- 忽略：符合 `.gitignore` 规则的文件不会被默认跟踪。
- 删除和重命名也会形成 Git 变更，具体识别取决于内容相似度。

## 7. 第一次提交流程

```bash
git status
git add README.md
git commit -m "docs: add project readme"
git log --oneline --decorate
```

- `git status` 用于确认当前状态和下一步操作。
- `git add` 把指定变更放入暂存区。
- `git commit` 创建新的提交对象。
- 提交信息应说明“做了什么”和“为什么”，保持简洁明确。
- `git log` 查看提交历史，`--oneline` 和 `--decorate` 可提升可读性。
