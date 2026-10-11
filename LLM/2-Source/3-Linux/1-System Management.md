---
order: 1
tags: [Linux, 系统管理]
next: "[[2-Shell Scripting]]"
---

## 本章大纲

- [[#1. Linux 系统与发行版]]
- [[#2. 用户与组管理]]
- [[#3. 文件权限管理]]
- [[#4. 进程管理]]
- [[#5. 系统服务管理]]
- [[#6. 文件系统与磁盘管理]]
- [[#7. 软件包管理]]
- [[#8. 系统优化与资源限制]]

## 1. Linux 系统与发行版

- Linux 内核负责进程调度、内存管理、文件系统、设备驱动和网络协议栈等核心功能。
- 发行版由内核、系统工具、软件包管理器和桌面环境等组成。
- 常见发行版包括 `CentOS`、`RHEL`、`Ubuntu`、`Debian`、`SUSE` 等。
- 服务器场景更关注稳定性、长期支持、安全更新和软件生态。
- Linux 目录遵循 `FHS` 标准，常见目录包括 `/etc`、`/var`、`/usr`、`/opt`、`/home`。
- `root` 是超级用户，日常运维应避免长期直接使用高权限账号。

## 2. 用户与组管理

```bash
useradd -m -s /bin/bash alice
passwd alice
groupadd developers
usermod -aG developers alice
id alice
```

- `useradd` 创建用户，`usermod` 修改用户属性，`userdel` 删除用户。
- `passwd` 管理密码，`chage` 管理密码有效期和过期策略。
- `groupadd`、`groupmod`、`groupdel` 管理用户组。
- `id`、`whoami`、`groups` 可查看当前用户和组成员关系。
- `/etc/passwd` 保存用户基本信息，`/etc/shadow` 保存密码哈希，`/etc/group` 保存组信息。
- 应遵循最小权限原则，只授予完成任务所需的权限。

## 3. 文件权限管理

### 基本权限

```bash
chmod 750 script.sh
chown alice:developers data.txt
```

- 权限分为读 `r`、写 `w`、执行 `x`，分别作用于属主、属组和其他用户。
- 数字权限中 `r=4`、`w=2`、`x=1`，例如 `750` 表示属主读写执行、属组读执行、其他无权限。
- `chmod` 修改权限，`chown` 修改属主和属组，`chgrp` 修改属组。
- `umask` 决定新建文件和目录的默认权限。
- 特殊权限包括 `SUID`、`SGID` 和粘滞位 `Sticky Bit`。
- `setfacl` 和 `getfacl` 可配置更细粒度的访问控制列表。

## 4. 进程管理

```bash
ps aux
top
pgrep nginx
kill -15 PID
```

- `ps` 查看进程快照，`top` 和 `htop` 动态查看资源占用。
- `pgrep`、`pidof`、`pstree` 用于按名称或关系查找进程。
- `kill -15` 请求进程正常退出，`kill -9` 强制终止且可能造成数据损坏。
- `nice` 和 `renice` 调整进程优先级。
- `jobs`、`bg`、`fg` 管理当前终端的后台任务。
- `nohup`、`systemd` 或终端复用工具适合运行长期任务。
- 排查进程时应同时观察 CPU、内存、文件描述符、网络连接和日志。

## 5. 系统服务管理

```bash
systemctl status nginx
systemctl start nginx
systemctl enable nginx
journalctl -u nginx
```

- `systemd` 是现代 Linux 发行版常用的初始化系统和服务管理器。
- `systemctl status` 查看服务状态，`start`、`stop`、`restart`、`reload` 控制服务。
- `enable` 和 `disable` 控制系统启动时是否自动运行。
- `daemon-reload` 在修改 unit 文件后重新加载配置。
- 服务配置通常位于 `/etc/systemd/system` 或 `/usr/lib/systemd/system`。
- 服务异常时应检查状态、单元文件、依赖项和日志。

## 6. 文件系统与磁盘管理

```bash
lsblk
df -h
du -sh /var/log
mount /dev/sdb1 /mnt/data
```

- 常见文件系统包括 `ext4`、`xfs`、`btrfs` 等。
- `fdisk`、`parted` 用于分区管理，`mkfs` 用于创建文件系统。
- `mount` 和 `umount` 挂载、卸载文件系统。
- `/etc/fstab` 用于配置开机自动挂载，修改前应备份并验证。
- `df` 查看文件系统空间，`du` 统计目录占用，`lsblk` 查看块设备。
- `fsck` 用于检查和修复文件系统，通常应在卸载或救援环境中执行。
- `LVM` 通过物理卷、卷组和逻辑卷提供灵活扩容能力。

## 7. 软件包管理

### Debian / Ubuntu

```bash
apt update
apt install nginx
apt remove nginx
```

### RHEL / CentOS / Fedora

```bash
dnf install nginx
dnf update
rpm -qa
```

- `apt` 和 `dpkg` 用于 Debian 系发行版，`dnf`/`yum` 和 `rpm` 用于 RHEL 系发行版。
- 安装前应更新软件源索引，生产环境升级前应评估兼容性和回滚方案。
- 软件源配置通常位于 `/etc/apt/sources.list*` 或 `/etc/yum.repos.d/`。
- 应优先使用发行版仓库和安全更新，减少不可信第三方源。
- 使用 `rpm -V`、`dpkg -V` 可检查已安装文件是否被修改。

## 8. 系统优化与资源限制

- `sysctl` 用于查看和调整内核参数，永久配置通常写入 `/etc/sysctl.d/` 或 `/etc/sysctl.conf`。
- `ulimit` 控制进程可使用的文件描述符、进程数和内存等资源。
- `/etc/security/limits.conf` 可配置用户级资源限制。
- `swappiness` 影响交换空间使用倾向，调整前要结合内存和业务特性。
- 优化前先测量 CPU、内存、磁盘和网络瓶颈，避免盲目修改内核参数。
- 任何系统级调整都应在测试环境验证，并记录变更和回滚方法。
