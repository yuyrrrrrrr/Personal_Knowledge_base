---
order: 7
tags: [Linux, 自动化运维]
prerequisites: ["[[6-Security Reinforce]]"]
---

## 本章大纲

- [[#1. 自动化运维基础]]
- [[#2. Ansible 基础]]
- [[#3. Ansible 模块与 Playbook]]
- [[#4. 配置管理与编排]]
- [[#5. Docker 基础]]
- [[#6. Kubernetes 基础]]
- [[#7. CI/CD 与自动化流程]]
- [[#8. 安全与最佳实践]]

## 1. 自动化运维基础

- 自动化用于减少重复操作、降低人为错误并提高交付效率。
- 自动化对象包括配置、部署、巡检、备份、扩缩容和故障处理。
- 幂等性要求同一操作执行多次结果保持一致。
- 自动化任务应有输入校验、日志、超时、重试和失败回滚。
- 先梳理流程并验证手工步骤，再把稳定流程脚本化。
- 自动化不是无人监管，仍需监控、审计、告警和人工兜底。

## 2. Ansible 基础

```bash
ansible all -i inventory.ini -m ping
ansible-playbook -i inventory.ini site.yml
```

- Ansible 通常基于 SSH 无代理工作，适合中小规模和传统服务器环境。
- `inventory` 定义主机、主机组和连接信息。
- `ansible.cfg` 控制默认配置，`ansible-doc` 查看模块文档。
- `ad-hoc` 命令适合临时任务，Playbook 适合可复用流程。
- `--check` 可以预演，`--diff` 可以查看配置差异。
- 密钥认证、主机分组和权限控制是自动化安全的基础。

## 3. Ansible 模块与 Playbook

```yaml
- name: 安装并启动 Nginx
  hosts: web
  become: true
  tasks:
    - name: 安装 nginx
      package:
        name: nginx
        state: present
    - name: 启动 nginx
      service:
        name: nginx
        state: started
        enabled: true
```

- 常用模块包括 `package`、`service`、`copy`、`template`、`file`、`command`、`shell`、`user`。
- 优先使用幂等模块，只有必要场景才使用 `command` 或 `shell`。
- `handlers` 用于配置变化后触发重启或重载。
- `variables`、`facts`、`templates` 和 `roles` 提升复用性和可维护性。
- `tags` 可选择执行部分任务，`serial` 可控制滚动更新批次。
- Playbook 应加入语法检查、测试环境和失败回滚策略。

## 4. 配置管理与编排

- 配置管理确保服务器长期保持期望状态，而不是只执行一次命令。
- Ansible 是推荐优先掌握的工具，Puppet 和 Chef 可按现有环境选择性学习。
- 配置和代码应纳入版本控制，所有变更可审计、可回滚。
- 角色和模块应职责清晰，避免把所有逻辑堆在单个 Playbook 中。
- 自动化任务要支持并发限制、失败中止和局部重试。
- 变更前记录当前状态，变更后验证服务、端口、日志和业务结果。

## 5. Docker 基础

```bash
docker images
docker ps
docker run -d --name web -p 8080:80 nginx
docker logs web
```

- 镜像包含应用及运行依赖，容器是镜像的运行实例。
- Dockerfile 用于构建镜像，应使用明确的基础镜像版本。
- 容器数据通过 volume 或 bind mount 持久化。
- 通过环境变量和配置文件注入运行参数，不把密钥写入镜像。
- Docker Compose 适合编排单机多容器应用。
- 容器日志要设置驱动、轮转和容量限制，避免占满磁盘。

## 6. Kubernetes 基础

```bash
kubectl get nodes
kubectl get pods -A
kubectl apply -f deployment.yaml
```

- Kubernetes 用于容器调度、服务发现、副本管理、滚动更新和自愈。
- 常见资源包括 `Pod`、`Deployment`、`Service`、`Ingress`、`ConfigMap`、`Secret`。
- `kubectl` 是主要命令行工具，`describe` 和 `logs` 是排障入口。
- 资源应配置 requests、limits、探针和副本策略。
- 生产环境要关注命名空间、RBAC、网络策略、存储和集群备份。
- 应用部署应支持灰度、回滚、健康检查和可观测性。

## 7. CI/CD 与自动化流程

- CI 持续集成代码、构建、测试和质量检查。
- CD 持续交付或部署把通过验证的产物发布到目标环境。
- 流水线通常包括拉取代码、依赖安装、测试、构建镜像、扫描、部署和验证。
- 构建产物应版本化并保存，避免每次部署重新构建。
- 环境配置与业务代码分离，使用审批、灰度、回滚和变更记录控制风险。
- Jenkins、GitLab CI、GitHub Actions 等工具可按团队技术栈选择。

## 8. 安全与最佳实践

- 自动化凭据使用密钥管理、临时令牌或受限服务账号。
- 最小权限原则同样适用于 Ansible、容器、Kubernetes 和 CI/CD。
- 对镜像、依赖、配置和脚本进行安全扫描。
- 关键操作增加审批、审计日志和人工确认。
- 自动化流程必须可观测、可回滚、可重复，并在测试环境验证。
- 自动化工具只是手段，稳定的流程、数据保护和故障预案才是核心。
