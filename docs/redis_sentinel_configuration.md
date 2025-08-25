# 用户管理 Redis 哨兵模式二进制配置指南

本文档详细说明了用户管理在二进制环境中的哨兵模式缓存配置方案，以提高 Redis 的高可用性。

## 配置变更概述

### 新增配置项

在 `src/build/api/support-files/templates/api#bkuser_core#config#overlays#prod.py` 中新增了以下配置项：

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `REDIS_MODE` | Redis 模式，可选值：`standalone`（单机模式）、`sentinel`（哨兵模式） | `sentinel` |
| `REDIS_SENTINEL_HOSTS` | 哨兵节点地址列表，用逗号分隔 | `"10.0.0.1:26379,10.0.0.2:26379,10.0.0.3:26379"` |
| `REDIS_SENTINEL_MASTER_NAME` | 哨兵主节点名称 | `"mymaster"` |
| `REDIS_SENTINEL_PASSWORD` | 哨兵密码（可选） | `"sentinel_password"` |

### 保留的原有配置项

| 配置项 | 说明 | 备注 |
|--------|------|------|
| `REDIS_HOST` | Redis 主机地址 | 单机模式使用 |
| `REDIS_PORT` | Redis 端口 | 单机模式使用 |
| `REDIS_PASSWORD` | Redis 数据库密码 | 两种模式都使用 |
| `REDIS_DB` | Redis 数据库编号 | 两种模式都使用 |
| `REDIS_KEY_PREFIX` | Redis 键前缀 | 两种模式都使用 |

## 配置示例

### 单机模式配置（默认）

```bash
# Redis 配置
BK_USERMGR_REDIS_MODE="standalone"
BK_USERMGR_REDIS_HOST="127.0.0.1"
BK_USERMGR_REDIS_PORT="6379"
BK_USERMGR_REDIS_PASSWORD="redis_password"
```

### 哨兵模式配置

```bash
# Redis 哨兵模式配置
BK_USERMGR_REDIS_MODE="sentinel"
BK_USERMGR_REDIS_SENTINEL_HOSTS="10.0.0.1:26379,10.0.0.2:26379,10.0.0.3:26379"
BK_USERMGR_REDIS_SENTINEL_MASTER_NAME="bk-redis-master-"
BK_USERMGR_REDIS_PASSWORD="redis_password"
BK_USERMGR_REDIS_SENTINEL_PASSWORD="sentinel_password"  # 可选
```

## 部署配置说明

### 1. 环境变量设置

在部署时，需要设置相应的环境变量或在配置文件中替换对应的占位符：

**单机模式：**
- `__BK_USERMGR_REDIS_MODE__` → `standalone`
- `__BK_USERMGR_REDIS_HOST__` → Redis服务器地址
- `__BK_USERMGR_REDIS_PORT__` → Redis服务器端口
- `__BK_USERMGR_REDIS_PASSWORD__` → Redis密码

**哨兵模式：**
- `__BK_USERMGR_REDIS_MODE__` → `sentinel`
- `__BK_USERMGR_REDIS_SENTINEL_HOSTS__` → 哨兵节点列表
- `__BK_USERMGR_REDIS_SENTINEL_MASTER_NAME__` → 哨兵主节点名称
- `__BK_USERMGR_REDIS_PASSWORD__` → Redis数据库密码
- `__BK_USERMGR_REDIS_SENTINEL_PASSWORD__` → 哨兵密码（可选）

### 2. 哨兵节点格式

哨兵节点列表格式为：`"host1:port1,host2:port2,host3:port3"`

如果不指定端口，将使用默认端口 26379。

示例：
- `"10.0.0.1:26379,10.0.0.2:26379,10.0.0.3:26379"`
- `"redis-sentinel-1,redis-sentinel-2,redis-sentinel-3"` （使用默认端口）

### 3. 配置验证

部署后可以通过以下方式验证配置是否正确：

1. 检查应用日志，确认 Redis 连接正常
2. 访问应用功能，验证缓存功能正常工作
3. 模拟 Redis 主节点故障，验证哨兵自动切换功能

## 故障排查

### 常见问题

1. **连接失败**
   - 检查哨兵节点地址和端口是否正确
   - 确认网络连通性
   - 验证密码设置

2. **主从切换异常**
   - 检查哨兵配置是否正确
   - 确认哨兵节点数量为奇数（建议3个或5个）
   - 查看哨兵日志

3. **缓存功能异常**
   - 检查 Redis 数据库编号是否正确
   - 确认 Redis 键前缀设置
   - 验证 Redis 权限配置

### 日志查看
通过查看日志可以获取详细的连接状态和错误信息。

# 用户管理 Redis 哨兵模式容器化配置指南

## 概述

本文档详细说明了用户管理在容器化部署环境中的哨兵模式缓存配置方案，以提高 Redis 的高可用性。

## 容器化部署

### 1. 部署配置

**BK-User API哨兵模式配置：**
在bkuser-values.yaml.gotmpl文档的api部分新增以下环境变量：
```yaml
    env:
    # 增加以下Redis哨兵配置
    - name: CACHE_REDIS_SENTINEL_ENABLED
        value: "true"
    - name: CACHE_REDIS_SENTINEL_MASTER_NAME
        value: "bk-redis-master-0"
    - name: CACHE_REDIS_SENTINEL_NODES
        value: "redis-sentinel-0:26379,redis-sentinel-1:26379,redis-sentinel-2:26379"
    - name: CACHE_REDIS_SENTINEL_PASSWORD
        value: ""  # 如果有密码
    - name: CACHE_REDIS_PASSWORD
        valueFrom:
        secretKeyRef:
            name: redis-secret
            key: password
```

## 配置参数详解

### Redis基础配置

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `CACHE_REDIS_HOST` | Redis主机地址 | 无 | `redis` |
| `CACHE_REDIS_PORT` | Redis端口 | 无 | `6379` |
| `CACHE_REDIS_PASSWORD` | Redis密码 | 无 | `sentinel_password` |
| `CACHE_REDIS_DB` | 数据库编号 | `0` | `0` |
| `CACHE_REDIS_KEY_PREFIX` | 键前缀 | `bk-user-` | `bk-user-` |

### Redis哨兵配置

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `CACHE_REDIS_SENTINEL_ENABLED` | 启用哨兵模式 | `false` | `true` |
| `CACHE_REDIS_SENTINEL_MASTER_NAME` | 主节点名称 | `bk-redis-master-0` | `bk-redis-master-0` |
| `CACHE_REDIS_SENTINEL_NODES` | 哨兵节点列表 | `[]` | `["sentinel1:26379", "sentinel2:26379"]` |
| `CACHE_REDIS_SENTINEL_PASSWORD` | 哨兵密码 | 无 | `sentinel_password` |

### Redis TLS配置

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `CACHE_REDIS_TLS_ENABLED` | 启用TLS | `false` | `true` |
| `CACHE_REDIS_TLS_CERT_CA_FILE` | CA证书文件 | 无 | `/certs/ca.crt` |
| `CACHE_REDIS_TLS_CERT_FILE` | 客户端证书 | 无 | `/certs/client.crt` |
| `CACHE_REDIS_TLS_CERT_KEY_FILE` | 客户端私钥 | 无 | `/certs/client.key` |

### 缓存策略配置

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `GLOBAL_CACHES_TIMEOUT` | 全局缓存超时时间（秒） | `3600` | `7200` |

## 监控和日志

### 1. Redis监控指标

- 内存使用率
- 连接数
- 命令执行速度
- 键过期情况
- 主从同步状态
