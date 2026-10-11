---
order: 3
tags: [Git, 分支管理]
prerequisites: ["[[2-Core Operations]]"]
next: "[[4-Remote Collaboration]]"
---

## 本章大纲

- [[#1. 分支基础]]
- [[#2. 分支创建与切换]]
- [[#3. 分支查看、重命名与删除]]
- [[#4. 分支合并与冲突]]
- [[#5. 变基操作]]
- [[#6. 交互式变基]]
- [[#7. 分支策略]]

## 1. 分支基础

- 分支本质上是指向某个提交的可移动引用。
- `HEAD` 通常指向当前分支，分支提交后会向前移动。
- 创建分支不会复制整个项目，只是增加一个引用。
- 分支适合隔离功能开发、修复、实验和发布准备。
- 本地分支和远程分支是不同引用，远程分支通常以 `origin/` 开头。
- 分支名称应清晰表达用途，例如 `feature/login`、`fix/payment-timeout`。

## 2. 分支创建与切换

```bash
git branch feature/login
git switch feature/login
git switch -c feature/payment
git checkout -b feature/search
```

- `git branch 名称` 创建分支但不切换。
- `git switch 名称` 切换分支。
- `git switch -c 名称` 创建并切换。
- `git checkout -b` 是旧式创建并切换写法。
- `git switch` 只处理分支切换，语义更清晰。
- 切换前应处理未提交修改，避免文件冲突或切换失败。

## 3. 分支查看、重命名与删除

```bash
git branch
git branch -a
git branch -vv
git branch -m old-name new-name
git branch -d finished-feature
```

- `git branch` 查看本地分支，`-a` 查看本地和远程分支。
- `git branch -vv` 查看分支指向的提交和跟踪关系。
- `git branch -m` 重命名分支。
- `git branch -d` 只删除已经合并的分支。
- `git branch -D` 强制删除未合并分支，应确认提交已备份或有其他引用。
- 删除本地分支不会删除远程分支，远程删除需要单独推送删除操作。

## 4. 分支合并与冲突

```bash
git switch main
git merge feature/login
```

- 快进合并：目标分支没有分叉时，只移动分支指针。
- 三方合并：双方都有新提交时创建合并提交。
- `--no-ff` 可以强制创建合并提交，保留功能分支边界。
- 合并冲突表示 Git 无法自动决定最终内容。
- 冲突文件中的 `<<<<<<<`、`=======`、`>>>>>>>` 标记需要手动解决。
- 解决冲突后执行 `git add`，再使用 `git commit` 或继续合并。
- 合并前应更新目标分支并运行测试，减少集成风险。

## 5. 变基操作

```bash
git switch feature/login
git rebase main
```

- 变基把当前分支的提交按新基点重新应用。
- 变基可以得到更线性的历史，但会生成新的提交哈希。
- 已经共享的分支通常不应变基，否则会影响其他协作者。
- 冲突时需要逐个解决并使用 `git rebase --continue` 继续。
- `git rebase --abort` 可以放弃本次变基。
- 变基与合并的选择应基于团队历史规范和协作方式。

## 6. 交互式变基

```bash
git rebase -i HEAD~3
```

- `pick` 保留提交，`reword` 修改提交信息。
- `edit` 暂停以修改提交内容，`squash` 合并到前一个提交。
- `fixup` 合并内容但丢弃当前提交信息。
- `drop` 删除提交。
- 交互式变基常用于整理本地提交、压缩修复提交和调整顺序。
- 重写共享历史前必须确认没有其他人依赖这些提交。

## 7. 分支策略

- Feature Branch：每个功能使用独立分支，完成后合并。
- Gitflow：使用 `main`、`develop`、`feature`、`release`、`hotfix` 等分支。
- GitHub Flow：从主分支创建短生命周期分支，通过 Pull Request 合并。
- Trunk-Based：开发者频繁向主干集成，配合短分支和自动化测试。
- 分支策略应与团队规模、发布节奏和测试能力匹配。
- 无论采用哪种策略，都应限制分支生命周期并及时清理。
