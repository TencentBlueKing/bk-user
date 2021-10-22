# Bk-User-Helm-Stack

Bk-User-Helm-Stack 是一个旨在快速部署用户管理部署工具，它在 Helm Chart 的基础上开发，旨在为用户管理产品提供方便快捷的部署能力。

## 准备依赖服务

要部署蓝鲸用户管理，首先需要准备 1 个 Kubernetes 集群（版本 1.12 或更高），并安装 Helm 命令行工具（版本 3.0 或更高）。

我们使用 `Ingress` 对外提供服务访问，所以请在集群中至少安装一个可用的 [Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)

### 配置 Helm 仓库地址
```bash
# 请将 `<HELM_REPO_URL>` 替换为 Chart 所在的 Helm 仓库地址
helm repo add bk-paas3 `<HELM_REPO_URL>`
helm repo update
```

### 其他服务
由于蓝鲸用户管理 SaaS 是需要校验用户身份的服务，所以在能够正常访问前，请确认以下服务已就绪：

- [蓝鲸登录](https://github.com/Tencent/bk-PaaS/tree/master/paas-ce/paas/login)
- [蓝鲸权限中心](https://github.com/TencentBlueKing/bk-iam)


## 快速安装

### 准备 `values.yaml`

#### 1. 获取蓝鲸平台访问地址 
首先，你需要获取到蓝鲸平台的访问地址，例如 `https://paas.example.com`，确保 `https://paas.example.com/login` 可以访问蓝鲸登录，然后将该值的内容填入全局环境变量中。

配置示例：
```yaml
global:
  env:
    # 蓝鲸平台域名
    BK_PAAS_URL: "https://paas.example.com"
```

#### 2. 确定用户管理访问地址

你需要为用户管理提供一个访问根域，类似 `example.com`，配置示例:
```yaml
global:
  sharedDomain: "example.com"
```

默认地，我们会为 `Api` & `SaaS` 分别创建两个访问入口(Ingress)：
- `bkuser.example.com` SaaS 页面访问入口
- `bkuser-api.example.com` Api 访问入口

#### 3. 准备用户管理镜像

用户管理官方提供了两个镜像：
```text
ccr.ccs.tencentyun.com/bk.io/bk-user-api:${version}
ccr.ccs.tencentyun.com/bk.io/bk-user-saas:${version}
```
我们会在每次发布用户管理新版时，会同步更新 Chart 中的镜像版本，所以如果你只是想使用最新版本的官方镜像，可以跳过此节，不用关注镜像的填写。

如果你想使用官方其他版本或者自己构建的镜像，也可以在 `values.yaml` 中修改，配置示例：
```yaml
global:
  image:
    # 修改镜像地址，我们会按照 {registry}/{repository} 方式拼接
    registry: any-mirrors-you-want.com/any-group
    # 修改用户管理版本，从 https://github.com/TencentBlueKing/bk-user/releases 获取
    tag: "v2.3.0"
```

#### 4. 数据库依赖

我们为**功能快速验证**提供了内嵌的 `mariadb` 组件，但我们并不保证该数据库的高可用性，所以***不建议在生产环境中直接使用***。

如果你没有数据库方面的特殊要求，那么不需要关注以下 `mariadb` 的默认配置。

```yaml
mariadb:
  enabled: true
  architecture: standalone
  auth:
    rootPassword: "root"
    username: "bk-user"
    password: "root"
  primary:
    # 默认我们未开启持久化，如有需求可以参考: https://kubernetes.io/docs/user-guide/persistent-volumes/
    persistence:
      enabled: false
  initdbScriptsConfigMap: "bk-user-mariadb-init
```

如果你想要在生产环境中使用其他外部数据库，那么可以通过环境变量来指定，并禁用 `mariadb`，配置示例:

```yaml
bkuserapi:
  enabeld: true
  env:
    # 手动指定外部 DB ，仅支持 MySQL/MariaDB
    DB_NAME: "your-db-name"
    DB_USER: "your-db-user"
    DB_PASSWORD: "your-db-password"
    DB_HOST: "your-db-host"
    DB_PORT: "your-db-port"
    # 外部 Celery Broker，任意符合要求的 Broker 存储均可
    CELERY_BROKER_URL: "your-broker-url"
    CELERY_RESULT_BACKEND: "your-broker-url"
  # 手动取消内建存储挂载
  envFrom: []

bkusersaas:
  enabled: true
  env:
    DB_NAME: "your-db-name"
    DB_USER: "your-db-user"
    DB_PASSWORD: "your-db-password"
    DB_HOST: "your-db-host"
    DB_PORT: "your-db-port"
  # 手动取消内建存储挂载 
  envFrom: []

mariadb:
  enabled: false
  
redis:
  enabled: false
```

#### 5. 权限中心
默认地，我们未开启权限中心，如果在权限中心已经就绪之后，想体验用户管理功能，那么你可以手动向权限中心注册模型:
```yaml
bkuserapi:
  env:
    # 填充权限中心相关变量
    BK_IAM_V3_INNER_HOST: "https://iam.example.com" 
  # 打开权限中心模型注册，每次重新部署即会运行
  preRunHooks:
    bkiam-migrate:
      enabled: true

bkusersaas:
  env:
    # 主动开启用户管理 SaaS 权限校验 
    DISABLE_IAM: false
```

#### 6. 账号密码
我们需要为 `admin` 账户添加用户名密码，虽然我们给定了默认值，但是为了安全，请手动修改：
```yaml
bkuserapi:
  env:
    # !!!请修改初始账号密码!!!
    INITIAL_ADMIN_USERNAME: "your-user-name"
    INITIAL_ADMIN_PASSWORD: "your-super-strong-password"
```

### 安装

如果你已经准备好了 `values.yaml`，就可以直接进行安装操作了

```bash
# 假定你想在 bk-user 命名空间安装
kubectl create namespace bk-user
helm install bk-user bk-user-stack -n bk-user -f values.yaml
```
安装过程中，命令行会预期**阻塞等待**数据库进行 `migrate` 操作：
- 首次安装时，会多次提示 `Pod api-on-migrate pending` 类似字样，原因是 `mariadb` 等待就绪耗时较长， `migrate` 容器会不断失败重试，请耐心等待。
- 升级安装时，会出现 `Pod api-on-migrate running` 类似字样，表示正在执行 `migrate` 操作，耗时一般在 10s 以内，具体视 migrate 内容而定，请耐心等待。

如果确认此次安装或更新无须变更数据库，可以临时手动关闭:
```bash
helm install bk-user bk-user-stack -n bk-user -f values.yaml \
 --set api.preRunHooks.db-migrate.enabled=false \
 --set saas.preRunHooks.db-migrate.enabled=false
```

如果在安装完成之后，访问 SaaS 地址出现 `503`，可以检查一下 `saas-web` 容器是否完全就绪，静候就绪后刷新页面即可。

## 卸载
```bash
# 卸载资源
helm uninstall bk-user -n bk-user

# 已安装的 mariadb & redis 并不会被删除，防止没有开启持久化期间产生的数据被销毁
# 如果确认已不再需要相关内容，可以手动删除命名空间内的资源
# 独立命名空间时
kubectl delete ns bk-user
# 非独立命名空间时
kubectl delete deploy,sts,cronjob,pod,svc,ingress,secret,cm,sa,role,rolebinding,pvc -l app.kubernetes.io/instance=bk-user -n bk-user 
```
