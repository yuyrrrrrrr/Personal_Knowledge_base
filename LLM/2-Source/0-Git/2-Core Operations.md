---
order: 2
tags: [Git, 核心操作]
prerequisites: ["[[1-Git Basics]]"]
next: "[[3-Branch Management]]"
---

## 本章大纲

- [[#1. 仓库创建与克隆]]
- [[#2. .git 目录与 .gitignore]]
- [[#3. 文件跟踪、暂存与提交]]
- [[#4. 查看状态、差异和历史]]
- [[#5. 撤销与恢复]]
- [[#6. reset、revert 与 restore]]
- [[#7. reflog 与误操作恢复]]

## 1. 仓库创建与克隆

```bash
git init
git init -b main
git clone https://example.com/team/project.git
git clone --depth 1 https://example.com/team/project.git
```

- `git init` 在当前目录创建 Git 仓库。
- `git init -b main` 可以在初始化时指定默认分支。
- `git clone` 下载远程仓库并自动配置 `origin`。
- `--depth 1` 创建浅克隆，只获取最近历史，适合构建和临时查看。
- 克隆后应先检查远程地址、默认分支和当前状态。
- 已有项目初始化时应先检查是否已经存在 `.git` 目录，避免嵌套仓库。

## 2. .git 目录与 .gitignore

`.git` 目录包含：

- `objects/`：保存 Git 对象。
- `refs/`：保存分支、标签和引用。
- `HEAD`：指向当前分支或提交。
- `index`：保存暂存区状态。
- `config`：仓库级配置。
- `logs/`：保存引用变更日志，可用于 `reflog`。

```gitignore
*.log
.env
node_modules/
__pycache__/
dist/
```

- `.gitignore` 只影响未被跟踪文件，已经跟踪的文件不会自动忽略。
- 忽略规则支持目录、通配符、否定规则和按目录生效。
- 忽略文件本身通常应提交，团队才能共享规则。
- 敏感文件和构建产物应尽早加入忽略规则。
- 已经提交的忽略文件需要先从索引移除，再提交规则变更。

## 3. 文件跟踪、暂存与提交

```bash
git add file.txt
git add .
git add -p
git commit -m "feat: add login validation"
git commit --amend
```

- `git add` 把工作区变更加入暂存区。
- `git add -p` 以补丁块方式选择性暂存。
- `git commit` 把暂存区内容写入本地历史。
- `git commit --amend` 修改最近一次提交，不适合已经共享的提交。
- 提交应保持单一目的，避免把无关修改混在一起。
- 提交信息推荐使用清晰的类型前缀，例如 `feat`、`fix`、`docs`、`refactor`。

## 4. 查看状态、差异和历史

```bash
git status
git diff
git diff --staged
git log --oneline --graph --decorate
git show HEAD
```

- `git status` 查看工作区和暂存区状态。
- `git diff` 比较工作区与暂存区，`git diff --staged` 比较暂存区与 HEAD。
- `git log` 查看提交历史，可结合 `--graph`、`--decorate`、`--stat`。
- `git show` 查看提交详情、作者、时间和差异。
- `git log -S "text"` 可以搜索引入或删除指定内容的提交。
- `git blame` 查看每行最后修改的提交和作者，但不能直接判断责任。

## 5. 撤销与恢复

```bash
git restore file.txt
git restore --staged file.txt
git checkout -- file.txt
```

- `git restore` 用于恢复工作区文件或取消暂存。
- `git restore --staged` 只把文件移出暂存区，不修改工作区内容。
- `git checkout -- file` 是旧式恢复命令，现代 Git 更推荐 `restore`。
- 恢复前先用 `git diff` 确认要丢弃的内容。
- 未提交的工作区修改被恢复后可能无法通过 Git 找回。
- 删除文件后可使用 `git restore` 或 `git checkout` 恢复。

## 6. reset、revert 与 restore

```bash
git reset --soft HEAD~1
git reset --mixed HEAD~1
git reset --hard HEAD~1
git revert HEAD
```

- `reset --soft`：移动 HEAD，保留暂存区和工作区。
- `reset --mixed`：移动 HEAD，重置暂存区，保留工作区，是默认模式。
- `reset --hard`：同时重置 HEAD、暂存区和工作区，可能丢失本地修改。
- `reset` 适合整理尚未共享的本地历史。
- `revert` 创建新提交来抵消旧提交，适合已经共享的历史。
- `restore` 更专注恢复文件内容，避免误用 `reset` 造成范围过大的影响。

## 7. reflog 与误操作恢复

```bash
git reflog
git reset --hard HEAD@{3}
git branch recovered HEAD@{3}
```

- `reflog` 记录本地 HEAD 和分支引用移动历史。
- 提交、重置、切换分支和变基都可能产生 reflog 记录。
- 误删分支或错误重置后，可以先通过 `reflog` 找到目标提交。
- 恢复前应先生成新分支或标记，避免再次覆盖目标提交。
- reflog 是本地的，不等于完整远程备份。
- `reset --hard` 前应保留工作区备份并确认影响范围。
