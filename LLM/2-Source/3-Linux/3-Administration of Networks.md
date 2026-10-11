---
order: 3
tags: [Linux, 网络管理]
prerequisites: ["[[2-Shell Scripting]]"]
next: "[[4-System Monitoring]]"
---

## 本章大纲

- [[#1. 网络基础]]
- [[#2. 网络接口与 IP 配置]]
- [[#3. DNS 与路由配置]]
- [[#4. 网络诊断工具]]
- [[#5. 抓包与性能分析]]
- [[#6. 防火墙管理]]
- [[#7. 网络故障排查]]

## 1. 网络基础

- 网络通信需要地址、路由、协议和端口共同配合。
- TCP/IP 模型主要包含网络接口层、网际层、传输层和应用层。
- IPv4 地址由网络部分和主机部分组成，子网掩码用于划分网络范围。
- 网关负责把数据包转发到其他网络，MAC 地址用于同一局域网内的链路寻址。
- TCP 面向连接、强调可靠传输，UDP 无连接、开销较小。
- 常见端口包括 SSH `22`、HTTP `80`、HTTPS `443`、MySQL `3306`。
- DNS 把域名解析为 IP 地址，常见记录包括 `A`、`AAAA`、`CNAME`、`MX`、`NS`。

## 2. 网络接口与 IP 配置

```bash
ip addr show
ip link show
ip route show
ip -s link
```

- `ip addr` 查看网卡和 IP 地址，`ip link` 查看链路状态。
- 临时添加地址：`ip addr add 192.168.1.10/24 dev eth0`。
- 启用接口：`ip link set eth0 up`；关闭接口时使用 `down`。
- `nmcli` 适合 NetworkManager 管理的桌面和服务器环境。
- Ubuntu 常见持久化配置位于 `netplan` YAML 文件。
- RHEL 系系统可使用 `nmcli` 或配置文件管理网络连接。
- 修改网络配置前应保留带外访问方式，避免远程连接中断。

## 3. DNS 与路由配置

```bash
cat /etc/resolv.conf
cat /etc/hosts
ip route add 10.0.0.0/8 via 192.168.1.1
```

- `/etc/hosts` 适合本地静态域名映射，优先级通常高于 DNS。
- `/etc/resolv.conf` 配置 DNS 解析器，但可能由 NetworkManager 或 systemd-resolved 管理。
- `ip route` 查看和调整路由表，默认路由通常标记为 `default`。
- `route -n` 是旧工具，现代系统优先使用 `ip route`。
- `dig`、`nslookup`、`host` 用于检查 DNS 解析和记录。
- DNS 故障要区分域名不存在、解析超时、错误 DNS 和缓存污染。

## 4. 网络诊断工具

- `ping`：检查目标 IP 或域名是否可达，并观察丢包和延迟。
- `traceroute`、`mtr`：查看数据包经过的路由和每跳延迟。
- `ss -tulnp`：查看监听端口和关联进程，`netstat` 是传统替代工具。
- `curl -v`：查看 HTTP 请求、响应头、连接和 TLS 交互过程。
- `dig`：检查 DNS 查询链路和响应记录。
- `telnet`、`nc`：测试目标主机端口是否可连接。
- `arp`、`ip neigh`：查看局域网邻居缓存和 MAC 地址映射。
- 排查顺序通常是从本机、网关、DNS、路由到目标服务逐层验证。

## 5. 抓包与性能分析

```bash
tcpdump -i eth0 -nn port 80
tcpdump -i any -w capture.pcap
```

- `tcpdump` 适合在服务器上按接口、协议、端口和主机过滤抓包。
- `wireshark` 适合图形化分析协议字段、请求响应和异常重传。
- `iftop`、`nethogs` 可以观察实时网络带宽和进程流量。
- 抓包文件可能包含敏感信息，应控制权限并及时清理。
- 分析网络性能时要关注延迟、抖动、丢包、重传、连接数和带宽。
- 高流量抓包可能影响系统性能，应设置过滤条件和抓包时长。

## 6. 防火墙管理

```bash
firewall-cmd --state
firewall-cmd --list-all
firewall-cmd --add-service=http --permanent
firewall-cmd --reload
```

- `iptables`、`nftables` 是 Linux 常见包过滤工具。
- `firewalld` 通过 zone、service 和 rich rule 管理规则。
- Ubuntu 常用 `ufw` 提供简化的防火墙操作。
- 规则设计应遵循最小开放原则，只允许必要来源、协议和端口。
- 云服务器还要检查安全组、网络 ACL 和主机防火墙，三者可能同时生效。
- 修改远程服务器防火墙前，应确保当前 SSH 会话不会被立即阻断。

## 7. 网络故障排查

- 先确认故障范围：单机、子网、数据中心、公网还是单个服务。
- 从物理链路、网卡状态、IP 地址、网关、DNS、路由和服务端口逐层检查。
- 使用 `ip`、`ping`、`traceroute`、`ss`、`curl`、`dig`、`tcpdump` 组合定位。
- 区分网络不通、端口未监听、防火墙拦截、DNS 解析错误和应用层错误。
- 记录现象、命令、结果、时间点和变更记录，便于复盘。
- 故障恢复后应补充监控、告警、自动化检查和防护措施。
