# bk-user Chart 安装说明

bk-user 是一个旨在快速部署用户管理部署工具，它在 Helm Chart 的基础上开发，旨在为用户管理产品提供方便快捷的部署能力。

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
  bkDomain: "example.com"
  bkDomainScheme: "http"

api:
  enabeld: true
  bkIamUrl: "http://bkiam.example.com"
  bkPaasUrl: "http://paas.example.com"
  bkComponentApiUrl: "http://bkapi.example.com"
  bkApiUrlTmpl: "http://bkapi.example.com/api/{api_name}"
  bkApigatewayPublicKey: ""

saas:
  enabled: true
  bkUserAddr: bkuser.example.com
  bkIamUrl: "http://bkiam.example.com"
  bkPaasUrl: "http://paas.example.com"
  bkComponentApiUrl: "http://bkapi.example.comm"

login:
  enabled: true
  bkPaas3Addr: "paas.example.com"
```

#### 2. 确定应用鉴权信息

需要以下 3 类鉴权信息:
- 用户管理应用 code (bk_user) 对应的 bk_app_secret
- 统一登录服务: bk_paas 对应的 bk_app_secret
- 统一登录服务: 32位随机字符串，用于加密登录态票据(bk_token)

你需要为用户管理提供一个访问根域，类似 `example.com`，配置示例:
```yaml
api:
  appCode: "bk_usermgr"
  appSecret: "some-app-secret"

saas:
  appCode: "bk_usermgr"
  appSecret: "some-app-secret"

login:
  # bk_paas 对应的 bk_app_secret 信息
  bkPaasSerectKey: "enter-paas-secret-key"
  # 32位随机字符串，用于加密登录态票据(bk_token)
  # tr -dc A-Za-z0-9 </dev/urandom | head -c 32 | base64
  encryptSecretKey: "somesecretkey"
```

#### 3. 准备用户管理镜像

我们会在每次发布用户管理新版时，会同步更新 Chart 中的镜像版本，所以如果你只是想使用最新版本的官方镜像，可以跳过此节，不用关注镜像的填写。

如果你想使用官方其他版本或者自己构建的镜像，也可以在 `values.yaml` 中修改，配置示例：
```yaml
api:
  image:
    registry: hub.bktencent.com
    repository: blueking/bk-user-api
    tag: "v2.3.1"

saas:
  image:
    registry: hub.bktencent.com
    repository: blueking/bk-user-saas
    tag: "v2.3.1"

login:
  image:
    registry: hub.bktencent.com
    repository: blueking/bk-login
    tag: "v2.3.1"
```

或者直接修改全局镜像变量

```yaml
global:
  imageRegistry: "some-custom-registry.com"
```

> 注意这里同时也会修改 bitnami 内建存储的 Registry

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
api:
  externalDatabase:
    default:
        host: ""
        password: ""
        port: 3306
        user: ""
        name: "bk_user_api"

saas:
  externalDatabase:
    default:
        host: ""
        password: ""
        port: 3306
        user: ""
        name: "bk_user_saas"

login:
  externalDatabase:
    default:
        host: ""
        password: ""
        port: 3306
        user: ""
        name: "bk_login"

mariadb:
  enabled: false

redis:
  enabled: false
```

#### 5. 权限中心
默认地，我们已开启权限中心，如果功能验证时想跳过权限中心，可以手动关闭
```yaml
global:
  enableIAM: false
```

#### 6. 账号密码
我们需要为 `admin` 账户添加用户名密码，虽然我们给定了默认值，但是为了安全，请手动修改：
```yaml
api:
  initialAdminUsername: "admin"
  initialAdminPassword: "Blueking@2019"
```

### 7. 蓝鲸日志采集配置

用于将容器日志和标准输出日志采集到蓝鲸日志平台。默认未开启，如需开启请将 `global.bkLogConfig.enabled` 设置为 true。

##### `values.yaml` 配置示例：
```yaml
global:
  bkLogConfig:
    enabled: true
    dataId: 1
```

### 8. 容器监控 Service Monitor

默认未开启，如需开启请将 `global.serviceMonitor.enabled` 设置为 true。

##### `values.yaml` 配置示例：

```yaml
global:
  serviceMonitor:
    enabled: true
```

### 9. 配置sentry

```yaml
global:
  ## sentry dsn
  sentryDsn: "http://12927b5f211046b575ee51fd8b1ac34f@{SENTRY_DOMAIN}/{PROJECT_ID}"
```

### 10. 开启api auth

默认值是true, 可以关闭, 关闭之后用户管理 API 将不受任何保护

开启之后, 只能通过 ESB 访问用户管理接口

注意, 配置文件中下面两个值必须一致, 并且如果开启, login必须配置组件访问地址`bkLoginApiAuthEnabled`

```yaml
global:
  ## 是否开启 API AUTH, 默认开启
  enableApiAuth: true

login:
  # Login API Auth Enabled 登录是否开启了 API 认证
  bkLoginApiAuthEnabled : true
  # 蓝鲸 ESB/APIGATEWAY url，注意集群内外都是统一域名。集群内可以配置域名解析到内网ip
  bkComponentApiUrl: "http://bkapi.example.com"
```

### 10. 安装

如果你已经准备好了 `values.yaml`，就可以直接进行安装操作了

```bash
# 假定你想在 bk-user 命名空间安装
kubectl create namespace bk-user
helm install bk-user bk-user -n bk-user -f values.yaml
```


如果在安装完成之后，访问 SaaS 地址出现 `503`，可以检查一下 `saas-web` 容器是否完全就绪，静候就绪后刷新页面即可。

## 资源释义
你可以通过 kubectl 获取安装详情:
```bash
# 获取所有 controller
kubectl get deploy,job,sts -l app.kubernetes.io/instance=bk-user
# 获取所有 Pod
kubectl get pod -l app.kubernetes.io/instance=bk-user
# 获取访问入口
kubectl get svc,ingress -l app.kubernetes.io/instance=bk-user
```

通常在安装后，我们会看到这些 Pod

| Pod 前缀                  | 所属模块      | 作用          |
|-------------------------|-----------|-------------|
| bk-login-web            | 蓝鲸登录      | 主进程         |
| bk-login-migrate-db     | 蓝鲸登录      | 初始化数据库作业    |
| bk-user-saas            | 用户管理 SaaS | 主进程         |
| bk-user-saas-migrate-db | 用户管理 SaaS | 初始化数据库作业    |
| bk-user-api-web         | 用户管理 API  | 主进程         |
| bk-user-api-worker      | 用户管理 API  | 后台任务进程      |
| bk-user-api-beat        | 用户管理 API  | 周期任务        |
| bk-user-api-migrate-db  | 用户管理 API  | 初始化数据库作业    |
| bk-user-api-migrate-db  | 用户管理 API  | 初始化数据库作业    |
| bk-user-api-migrate-iam | 用户管理 API  | 初始化权限中心模型作业 |

## 卸载
```bash
helm uninstall bk-user -n bk-user
```
