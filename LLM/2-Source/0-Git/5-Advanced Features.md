---
order: 5
tags: [Git, 高级特性]
prerequisites: ["[[4-Remote Collaboration]]"]
next: "[[6-Tools and Platforms]]"
---

## 本章大纲

- [[#1. 标签管理]]
- [[#2. 储藏功能]]
- [[#3. 子模块]]
- [[#4. 子树]]
- [[#5. 高级历史与对象操作]]

## 1. 标签管理

```bash
git tag
git tag -l "v1.*"
git tag -a v1.2.0 -m "release v1.2.0"
git show v1.2.0
git tag -d v1.2.0
git push origin v1.2.0
```

- 轻量标签只是一个提交引用，适合临时标记。
- 附注标签包含作者、日期和说明，适合正式发布。
- 标签应按语义化版本和团队规范命名。
- 本地标签不会自动推送到远程，需要单独推送。
- 删除远程标签会影响使用者，发布标签应尽量避免重建。
- 发布时应记录版本、变更、构建结果和相关提交。

## 2. 储藏功能

```bash
git stash push -m "wip login form"
git stash list
git stash show -p
git stash pop
git stash apply
```

- `stash` 临时保存工作区和暂存区修改，让工作区恢复干净。
- `stash push -m` 为该储藏添加说明，方便以后识别。
- `stash pop` 恢复并删除储藏，`stash apply` 恢复但保留储藏。
- `stash -u` 可以包含未跟踪文件。
- `stash -p` 可以交互选择部分修改。
- 储藏不是长期备份，恢复和冲突处理完成后应清理无用记录。

## 3. 子模块

```bash
git submodule add https://example.com/libs/common.git libs/common
git submodule update --init --recursive
git submodule status
```

- 子模块是在父仓库中引用另一个独立 Git 仓库。
- 父仓库记录子模块的提交哈希，而不是复制子仓库全部内容。
- 克隆父仓库后需要初始化并更新子模块。
- 子模块有独立提交、分支和远程配置，提交顺序容易出错。
- 修改子模块后，需要先提交子模块，再在父仓库提交新的指针。
- 子模块适合独立版本化和复用明确的依赖。

## 4. 子树

```bash
git subtree add --prefix=vendor/lib https://example.com/lib.git main --squash
git subtree pull --prefix=vendor/lib https://example.com/lib.git main --squash
```

- 子树把其他仓库内容合并到当前仓库的子目录。
- 与子模块不同，子树文件直接存在于父仓库历史中。
- 子树对使用者更简单，不需要额外初始化命令。
- `--squash` 可以把上游历史压缩为一个提交，减少历史体积。
- 子树适合希望把依赖内容纳入主仓库管理的场景。
- 子树和子模块都会增加同步复杂度，简单依赖应优先使用包管理器。

## 5. 高级历史与对象操作

```bash
git rev-parse HEAD
git cat-file -p HEAD
git fsck
git gc
```

- `rev-parse` 解析引用和提交表达式。
- `cat-file` 查看 Git 对象内容。
- `fsck` 检查对象完整性和悬空对象。
- `gc` 清理无用对象并优化仓库存储。
- `stash`、标签、子模块和子树都会产生额外引用，排查时要结合 `reflog` 和对象关系。
- 高级操作前应确认远程备份和本地仓库状态。
