# 蓝鲸用户管理核心 API 开发指引

## 将公共代码链接到 api 项目中

```
make link
```

## 安装依赖

进入对应目录，使用 [poetry](https://github.com/python-poetry/poetry) 安装依赖

``` bash
cd api/
poetry install
```

## 创建本地开发配置

本地开发需要创建两个文件：
```text
bkuser_core/config/common/.env
bkuser_core/config/overlays/dev.py
```

前者包含了项目启动的必须环境变量，我们已经默认为你创建了一个示例 `.env-tmpl`，它可能不能直接用于你的本地环境，你需要自行修改其中某些值(相信我，很简单的)。

后者我们同样提供了一个 `dev.tmpl`，你需要阅读它，并创建属于自己的 `dev.py`。

由于 `dev.py` 已经被添加到了 `.gitignore`，所以它不会被提交到版本仓库（也不应该）。

## 启动

进入对应目录，启动测试脚本
```bash
bin/start_dev.sh

# 如果需要测试后台相关功能
bin/start_celery.sh
bin/start_beat.sh
```

当项目运行起来之后，访问 `/redoc` 或 `/swagger` 路径获得所有 API 的详细说明。

同时当你修改了对应代码后，请运行 `make generate-sdk` 生成新的 SDK 文件，保证 `SaaS` 调用正常。

## 单元测试

### LDAP & MAD 测试

由于内置了 `Ldap & MAD` 的功能，所以需要额外配置资源

可以使用 `Docker` 来启动 `Ldap` 服务进行测试:

``` bash
# openLdap
docker run -p 389:389 -p 636:636 \ 
        --name my-openldap-container \
        --detach osixia/openldap:1.3.0

# ldap admin
docker run -p 6443:443 \
        --env PHPLDAPADMIN_LDAP_HOSTS=docker.for.mac.host.internal \
        --detach osixia/phpldapadmin:0.9.0
```

使用 `bkuser_core/tests/categories/vendors/ldap/assets/ldap.ldif` 直接导入必须的数据。

最后，在 `dev.py` 中配置

``` python
TEST_LDAP = {
    "url": "localhost",
    "base": "dc=example,dc=org",
    "user": "cn=admin,dc=example,dc=org",
    "password": "admin",
    "user_class": "inetOrgPerson",
    "organization_class": "organizationalUnit",
}
```
运行单元测试

``` bash
pytest bkuser_core/tests --disable-pytest-warnings --reuse-db
```

## 目录插件开发

针对数据同步和登陆，目录提供了一个插件能力，可以接受按照一定协议的用户自定义插件，具体内容请查阅 [数据源插件开发](/src/api/bkuser_core/categories/plugins/README.md)

## 国际化

每次添加新的字符串提示后，需要生成新的 `.po` 文件

``` bash
python manage.py makemessages --all
```

修改 `.po` 文件内的翻译内容后，编译 `.mo`

``` bash
python manage.py compilemessages -l en
python manage.py compilemessages -l zh-hans
```

## 关于缓存

用户管理默认是没有开启缓存能力的，可以通过环境变量控制缓存使用与否

``` bash
# 关闭缓存
export BK_USER_NO_CACHE=1
```
