# IDP 插件开发指南

## 目录

- [概述](#概述)
- [插件架构](#插件架构)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [开发身份凭证认证插件](#开发身份凭证认证插件)
- [开发联邦认证插件](#开发联邦认证插件)
- [配置和测试](#配置和测试)
- [Kubernetes 部署](#kubernetes-部署)

## 概述

IDP（Identity Provider）插件是蓝鲸用户管理系统的认证扩展机制，允许开发者自定义认证方式，对接各种第三方身份认证系统。

### 插件类型

本系统支持两种类型的认证插件：

| 类型 | 说明 | 适用场景 | 示例 |
|------|------|----------|------|
| **身份凭证认证** | 用户直接在登录页面输入凭证信息 | 简单的用户名密码认证、验证码登录 | 本地账密、LDAP、自定义 API |
| **联邦认证** | 重定向到第三方系统完成认证 | OAuth、SAML 等标准协议认证 | 企业微信、钉钉、OAuth 2.0 |

### 内置插件

系统`预计`会内置了以下插件：

- **身份凭证认证**
  - `local`: 本地账密登录
  - `ldap`: LDAP 认证
  - `mad`: Microsoft Active Directory

- **联邦认证**
  - `wecom`: 企业微信（自建应用）
  - `oauth2.0`: OAuth 2.0 标准协议
  - `oidc`: OpenID Connect
  - `saml2.0`: SAML 2.0 标准协议

### 自定义插件命名规范

⚠️ **重要**：自定义插件的 ID 必须以 `custom_` 为前缀，例如：
- ✅ `custom_my_plugin`
- ✅ `custom_oauth_gitlab`
- ❌ `my_plugin` （不符合规范）
- ❌ `local` （与内置插件冲突）

## 插件架构

### 项目结构

```
idp-plugins/
├── idp_plugins/                 # 插件包根目录
│   ├── __init__.py             # 自动加载所有插件
│   ├── base.py                 # 插件基类定义
│   ├── models.py               # 数据模型
│   ├── constants.py            # 常量定义
│   ├── exceptions.py           # 异常定义
│   ├── utils.py                # 工具函数
│   ├── http.py                 # HTTP 客户端
│   │
│   ├── local/                  # 本地账密插件（示例）
│   │   ├── __init__.py         # 插件注册
│   │   ├── plugin.py           # 插件实现
│   │   ├── client.py           # API 客户端
│   │   ├── settings.py         # 配置常量
│   │   └── logo.png            # 插件图标
│   │
│   ├── wecom/                  # 企业微信插件（示例）
│   │   ├── __init__.py
│   │   ├── plugin.py
│   │   ├── client.py
│   │   ├── settings.py
│   │   └── logo.png
│   │
│   └── custom_xxx/             # 自定义插件（您开发的）
│       ├── __init__.py
│       ├── plugin.py
│       ├── client.py           # 可选
│       ├── settings.py         # 可选
│       └── logo.png            # 可选
│
├── pyproject.toml              # 项目依赖配置
└── README.md                   # 本文档
```

### 核心类关系

```
BasePluginConfig                    # 配置基类（使用 Pydantic）
    └── sensitive_fields            # 敏感字段声明

BaseIdpPlugin                       # 插件基类
    ├── id                          # 插件唯一标识
    ├── config_class                # 配置类
    ├── dispatch_configs            # 扩展请求配置
    ├── test_connection()           # 连通性测试
    └── dispatch_extension()        # 扩展请求分发

    ├── BaseCredentialIdpPlugin     # 身份凭证认证插件
    │   └── authenticate_credentials()  # 验证凭证
    │
    └── BaseFederationIdpPlugin     # 联邦认证插件
        ├── build_login_uri()       # 构建登录跳转 URL
        └── handle_callback()       # 处理回调
```

## 快速开始

### 第一步：确定插件类型

根据您的认证需求选择合适的插件类型：

**选择身份凭证认证插件，如果：**
- 用户在蓝鲸登录页面直接输入凭证（用户名、密码、验证码等）
- 需要调用自定义 API 验证用户身份
- 不需要重定向到第三方系统

**选择联邦认证插件，如果：**
- 需要重定向到第三方系统（如企业微信、OAuth 服务）
- 使用标准的 OAuth、OIDC、SAML 等协议
- 需要支持单点登录（SSO）

### 第二步：创建插件目录

在 `src/idp-plugins/idp_plugins/` 目录下创建您的插件目录：

```bash
mkdir custom_my_plugin
```

创建必要的文件：

```bash
touch __init__.py plugin.py
```

可选文件：

```bash
touch client.py      # 如果需要调用第三方 API
touch settings.py    # 如果有配置常量
# 准备 logo.png（推荐尺寸：256x256，大小 < 64KB）
```

## 核心概念

### 配置类（Config Class）

配置类使用 [Pydantic](https://docs.pydantic.dev/) 定义，提供类型验证和数据校验功能。

```python
from ..base import BasePluginConfig

class MyPluginConfig(BasePluginConfig):
    # 根据插件所需自行定义必填字段，比如
    api_url: str
    api_key: str

    # 可选字段（带默认值），比如：
    timeout: int = 30
    enable_ssl: bool = True

    # 敏感字段（在 UI 中会被掩码显示）
    sensitive_fields = ["api_key"]
```

**敏感字段说明：**
- 字段的数据类型必须是 `str`
- 敏感字段在 UI 中显示为 `******`，更新时如果值不变则不会修改

### 插件注册

插件通过 `register_plugin()` 函数注册到系统：

```python
# __init__.py
from ..base import register_plugin
from .plugin import MyCustomPlugin

register_plugin(MyCustomPlugin)
```

系统启动时会自动扫描 `idp_plugins/` 目录下的所有子目录，并导入各插件的 `__init__.py`。

`注意`：idp_plugins 下 base.py / constants / ...等模块下的函数必须`相对路径方式 import`，因为插件会被 bk-user 和 bk-login 工程使用，若使用绝对路径，则无法满足多个工程同时使用（比如上面的 register_plugin）

### 异常处理

插件开发中应使用以下异常类型：

| 异常类 | 说明 | 使用场景 |
|--------|------|----------|
| `InvalidParamError` | 参数非法 | 请求参数缺失、格式错误 |
| `RequestAPIError` | API 请求失败 | 调用第三方 API 失败 |
| `ValidationError` | 校验不通过 | 数据校验失败 |
| `UnexpectedDataError` | 数据非预期 | 返回数据格式异常 |
| `ParseRequestBodyError` | 解析请求体失败 | JSON 解析错误 |

```python
from django.utils.translation import gettext_lazy as _

from ..exceptions import InvalidParamError, RequestAPIError

# 参数校验
if not username:
    raise InvalidParamError(_("用户名不能为空"))

# API 调用失败
try:
    response = api_call()
except Exception as e:
    raise RequestAPIError(_("认证失败：{}").format(str(e)))
```

### 工具函数

系统提供了常用的工具函数：

```python
from ..utils import (
    generate_random_str,      # 生成随机字符串
    parse_request_body_json,  # 解析 JSON 请求体
    urljoin,                  # 安全地拼接 URL
)

# 生成 32 位随机 state
state = generate_random_str(32)

# 解析请求体
request_body = parse_request_body_json(request.body)
username = request_body.get("username")

# 拼接 URL
url = urljoin("https://api.example.com", "/auth/login")
```

## 开发身份凭证认证插件

身份凭证认证插件适用于在登录页面直接输入凭证的场景。

### 完整示例

以下是一个完整的自定义 API 认证插件示例：

**plugin.py**

```python
# -*- coding: utf-8 -*-
from typing import Any, Dict
import requests

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ..base import BaseCredentialIdpPlugin, BasePluginConfig
from ..exceptions import InvalidParamError, RequestAPIError
from ..models import TestConnectionResult
from ..utils import parse_request_body_json, urljoin


class CustomApiPluginConfig(BasePluginConfig):
    """自定义 API 认证插件配置"""

    # API 基础地址
    api_base_url: str

    # API 密钥
    api_key: str

    # 超时时间（秒）
    timeout: int = 30

    # 是否验证 SSL 证书
    verify_ssl: bool = True

    # 声明敏感字段
    sensitive_fields = ["api_key"]


class CustomApiPlugin(BaseCredentialIdpPlugin):
    """自定义 API 认证插件"""

    # 插件唯一标识（必须以 custom_ 开头）
    id = "custom_api"

    # 配置类
    config_class = CustomApiPluginConfig

    def __init__(self, cfg: CustomApiPluginConfig):
        """初始化插件"""
        self.cfg = cfg
        # 可以在这里初始化 HTTP 客户端、数据库连接等
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        })

    def test_connection(self) -> TestConnectionResult:
        """
        连通性测试
        在配置页面点击"测试连接"按钮时调用
        """
        try:
            # 调用一个简单的健康检查接口
            url = urljoin(self.cfg.api_base_url, "/health")
            response = self.session.get(
                url,
                timeout=self.cfg.timeout,
                verify=self.cfg.verify_ssl
            )

            if response.status_code == 200:
                return TestConnectionResult(
                    ok=True,
                    message=_("连接成功")
                )
            else:
                return TestConnectionResult(
                    ok=False,
                    message=_("连接失败：HTTP {}").format(response.status_code)
                )

        except requests.exceptions.Timeout:
            return TestConnectionResult(
                ok=False,
                message=_("连接超时")
            )
        except requests.exceptions.SSLError:
            return TestConnectionResult(
                ok=False,
                message=_("SSL 证书验证失败")
            )
        except Exception as e:
            return TestConnectionResult(
                ok=False,
                message=_("连接失败：{}").format(str(e))
            )

    def authenticate_credentials(self, request: HttpRequest) -> Dict[str, Any]:
        """
        验证用户凭证
        这是插件的核心方法，在用户提交登录表单时调用

        :param request: Django HttpRequest 对象
        :return: 用户信息字典，用于匹配数据源用户
        """
        # 1. 解析请求体
        request_body = parse_request_body_json(request.body)

        # 2. 获取凭证信息
        username = request_body.get("username")
        password = request_body.get("password")

        # 3. 参数校验
        if not username:
            raise InvalidParamError(_("用户名不能为空"))

        if not password:
            raise InvalidParamError(_("密码不能为空"))

        # 4. 调用第三方 API 进行认证
        try:
            url = urljoin(self.cfg.api_base_url, "/auth/verify")
            response = self.session.post(
                url,
                json={
                    "username": username,
                    "password": password,
                },
                timeout=self.cfg.timeout,
                verify=self.cfg.verify_ssl
            )

            # 5. 处理响应
            if response.status_code == 200:
                user_data = response.json()

                # 6. 返回用户信息
                # 字段名可以自定义，后续在认证源配置中映射到数据源用户字段
                return {
                    "user_id": user_data.get("id"),
                    "username": user_data.get("username"),
                    "full_name": user_data.get("full_name"),
                    "email": user_data.get("email"),
                    "phone": user_data.get("phone"),
                }
            elif response.status_code == 401:
                raise RequestAPIError(_("用户名或密码错误"))
            elif response.status_code == 403:
                raise RequestAPIError(_("用户已被禁用"))
            else:
                raise RequestAPIError(
                    _("认证失败：HTTP {}").format(response.status_code)
                )

        except requests.exceptions.Timeout:
            raise RequestAPIError(_("认证请求超时"))
        except requests.exceptions.RequestException as e:
            raise RequestAPIError(_("认证请求失败：{}").format(str(e)))
        except Exception as e:
            raise RequestAPIError(_("认证过程发生错误：{}").format(str(e)))
```

**__init__.py**

```python
# -*- coding: utf-8 -*-
from ..base import register_plugin
from .plugin import CustomApiPlugin

# 注册插件
register_plugin(CustomApiPlugin)

# 注意：自定义插件还需要设置插件 Metadata 信息
from ..models import PluginMetadata

METADATA = PluginMetadata(
    # 插件唯一 ID（与插件类的 id 保持一致）
    id=CustomApiPlugin.id,
    # 插件展示用名称
    name="自定义 API 认证",
    # 插件展示用描述
    description="通过自定义 API 进行用户身份认证"
)
```

### 返回值说明

`authenticate_credentials()` 方法的返回值可以是：

1. **单个用户信息字典**（最常见）

```python
return {
    "user_id": "123456",
    "username": "zhangsan",
    "full_name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
}
```

2. **多个用户信息列表**（用于一个凭证对应多个用户的场景）

```python
return [
    {"user_id": "123", "username": "user1"},
    {"user_id": "456", "username": "user2"},
]
```

返回的字段会在认证源配置中映射到数据源用户字段。

## 开发联邦认证插件

联邦认证插件适用于需要重定向到第三方系统完成认证的场景。

### 完整示例：OAuth 2.0

以下是一个标准的 OAuth 2.0 认证插件示例：

**plugin.py**

```python
# -*- coding: utf-8 -*-
from typing import Any, Dict
from urllib.parse import urlencode
import requests

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ..base import BaseFederationIdpPlugin, BasePluginConfig
from ..exceptions import InvalidParamError, RequestAPIError
from ..models import TestConnectionResult
from ..utils import generate_random_str


class CustomOAuthPluginConfig(BasePluginConfig):
    """自定义 OAuth 2.0 插件配置"""

    # OAuth 客户端 ID
    client_id: str

    # OAuth 客户端密钥
    client_secret: str

    # 授权端点 URL
    authorization_endpoint: str

    # 令牌端点 URL
    token_endpoint: str

    # 用户信息端点 URL
    userinfo_endpoint: str

    # OAuth 权限范围
    scope: str = "openid profile email"

    # 超时时间（秒）
    timeout: int = 30

    # 声明敏感字段
    sensitive_fields = ["client_secret"]


class CustomOAuthPlugin(BaseFederationIdpPlugin):
    """自定义 OAuth 2.0 认证插件"""

    # 插件唯一标识
    id = "custom_oauth"

    # 配置类
    config_class = CustomOAuthPluginConfig


    def __init__(self, cfg: CustomOAuthPluginConfig):
        """初始化插件"""
        self.cfg = cfg

    @property
    def state_session_key(self) -> str:
        """
        State 参数的 Session Key
        用于防止 CSRF 攻击
        """
        return f"{self.id}_state"

    def test_connection(self) -> TestConnectionResult:
        """
        连通性测试
        可以尝试访问 OAuth 配置的各个端点
        """
        try:
            # 简单测试：访问授权端点看是否可达
            response = requests.get(
                self.cfg.authorization_endpoint,
                timeout=self.cfg.timeout
            )

            # OAuth 授权端点通常返回 400（缺少参数）而不是 404
            if response.status_code in [200, 400, 405]:
                return TestConnectionResult(
                    ok=True,
                    message=_("OAuth 配置验证成功")
                )
            else:
                return TestConnectionResult(
                    ok=False,
                    message=_("授权端点不可达：HTTP {}").format(response.status_code)
                )

        except Exception as e:
            return TestConnectionResult(
                ok=False,
                message=_("连接测试失败：{}").format(str(e))
            )

    def build_login_uri(self, request: HttpRequest, callback_uri: str) -> str:
        """
        构建跳转到 OAuth 服务的登录 URL

        :param request: Django HttpRequest，可以读写 Session
        :param callback_uri: OAuth 认证成功后的回调 URL（完整 URL）
        :return: OAuth 授权 URL
        """
        # 1. 生成随机 state 参数防止 CSRF 攻击
        state = generate_random_str(32)

        # 2. 将 state 保存到 Session
        request.session[self.state_session_key] = state

        # 3. 构建 OAuth 授权 URL 参数
        params = {
            "response_type": "code",
            "client_id": self.cfg.client_id,
            "redirect_uri": callback_uri,
            "scope": self.cfg.scope,
            "state": state,
        }

        # 4. 返回完整的授权 URL
        return f"{self.cfg.authorization_endpoint}?{urlencode(params)}"

    def handle_callback(self, request: HttpRequest) -> Dict[str, Any]:
        """
        处理 OAuth 回调

        :param request: Django HttpRequest，包含 code 和 state 参数
        :return: 用户信息字典
        """
        # 1. 验证 state 参数（防止 CSRF 攻击）
        state_in_session = request.session.get(self.state_session_key)
        state = request.GET.get("state")

        if not state or state != state_in_session:
            raise InvalidParamError(_("State 参数验证失败，可能存在 CSRF 攻击"))

        # 2. 获取授权码
        code = request.GET.get("code")
        if not code:
            # 检查是否有错误信息
            error = request.GET.get("error")
            error_description = request.GET.get("error_description", "")

            if error:
                raise InvalidParamError(
                    _("OAuth 授权失败：{} {}").format(error, error_description)
                )
            else:
                raise InvalidParamError(_("授权码不能为空"))

        # 3. 通过授权码获取访问令牌
        try:
            token_data = self._exchange_code_for_token(code, request)
            access_token = token_data.get("access_token")

            if not access_token:
                raise RequestAPIError(_("未能获取访问令牌"))

            # 4. 通过访问令牌获取用户信息
            user_info = self._get_user_info(access_token)

            return user_info

        except Exception as e:
            raise RequestAPIError(_("获取用户信息失败：{}").format(str(e)))

    def _exchange_code_for_token(
        self,
        code: str,
        request: HttpRequest
    ) -> Dict[str, Any]:
        """
        通过授权码换取访问令牌

        :param code: 授权码
        :param request: 请求对象（用于获取 callback_uri）
        :return: 令牌数据
        """
        # 构建回调 URL（需要与授权时的一致）
        callback_uri = request.build_absolute_uri(request.path)

        # 请求令牌端点
        response = requests.post(
            self.cfg.token_endpoint,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_uri,
                "client_id": self.cfg.client_id,
                "client_secret": self.cfg.client_secret,
            },
            headers={
                "Accept": "application/json",
            },
            timeout=self.cfg.timeout
        )

        if response.status_code != 200:
            raise RequestAPIError(
                _("获取访问令牌失败：HTTP {}").format(response.status_code)
            )

        return response.json()

    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        通过访问令牌获取用户信息

        :param access_token: 访问令牌
        :return: 用户信息
        """
        response = requests.get(
            self.cfg.userinfo_endpoint,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=self.cfg.timeout
        )

        if response.status_code != 200:
            raise RequestAPIError(
                _("获取用户信息失败：HTTP {}").format(response.status_code)
            )

        user_data = response.json()

        # 映射 OAuth 用户信息到标准字段
        return {
            "user_id": user_data.get("sub") or user_data.get("id"),
            "username": user_data.get("preferred_username") or user_data.get("username"),
            "full_name": user_data.get("name"),
            "email": user_data.get("email"),
        }
```

**__init__.py**

```python
# -*- coding: utf-8 -*-
from ..base import register_plugin
from .plugin import CustomOAuthPlugin

# 注册插件
register_plugin(CustomOAuthPlugin)

# 注意：自定义插件还需要设置插件 Metadata 信息
from ..models import PluginMetadata

METADATA = PluginMetadata(
    # 插件唯一 ID（与插件类的 id 保持一致）
    id=CustomOAuthPlugin.id,
    # 插件展示用名称
    name="自定义 OAuth 2.0",
    # 插件展示用描述
    description="通过 OAuth 2.0 协议进行联邦身份认证"
)
```

### Session 管理

联邦认证插件大部分时候都需要使用 Session 存储部分校验信息，比如 OAuth 的 state 参数

```python
@property
def state_session_key(self) -> str:
    """
    返回 Session Key
    建议格式：{plugin_id}_{key_name}
    确保不同插件、不同认证源之间不会冲突
    """
    return f"{self.id}_state"

def build_login_uri(self, request: HttpRequest, callback_uri: str) -> str:
    state = generate_random_str(32)

    # 保存到 Session
    request.session[self.state_session_key] = state

    # ... 构建 URL
    return authorization_url

def handle_callback(self, request: HttpRequest) -> Dict[str, Any]:
    # 从 Session 获取
    state_in_session = request.session.get(self.state_session_key)
    state = request.GET.get("state")

    # 验证
    if not state or state != state_in_session:
        raise InvalidParamError(_("State 参数验证失败"))

    # ...
```

## 配置和测试

### 本地开发集成测试

#### 1. 验证插件注册

```python
# 进入 Django shell
cd src/bk-user
python manage.py register_idp_plugin --dir_name=custom_my_plugin
```

#### 2. 启动开发环境

```bash
根据 bk-login / bk-user 本地环境搭建文档，运行登录和用户管理 SaaS 两个服务
```

#### 3. 在用户管理 SaaS 页面上配置认证源

1. 进入 "设置" -> "登录配置"
2. 点击 "对应的自定义认证源"
3. 填写配置参数
5. 保存认证源

#### 4. 测试登录流程

**身份凭证认证：**
1. 访问登录页面
2. 选择您的认证源
3. 输入测试用户名和密码
4. 提交表单
5. 验证是否成功登录

**联邦认证：**
1. 访问登录页面
2. 选择您的认证源
3. 点击登录按钮
4. 跳转到第三方系统
5. 完成第三方认证
6. 回调到系统
7. 验证是否成功登录


### 添加插件图标

为您的插件添加自定义图标可以提升用户体验：

1. **准备图标文件**
   - 文件名：`logo.png`
   - 推荐尺寸：256x256 像素
   - 文件大小：< 64KB（系统限制）
   - 格式：PNG

2. **放置图标文件**

```bash
cp your-logo.png src/idp-plugins/idp_plugins/custom_my_plugin/logo.png
```

3. **图标要求**
   - 背景透明
   - 主体居中
   - 简洁清晰
   - 适配深色/浅色主题

## Kubernetes 部署

如果您的服务是以 Kubernetes 方式部署的，需要通过 ConfigMap 的方式挂载自定义 IDP 插件。

### 第一步：打包插件为 ConfigMap

在 `src/idp-plugins` 目录下，使用 Makefile 命令打包插件：

```bash
cd src/idp-plugins

# 打包自定义 IDP 插件
# name 参数为插件目录名称（不是插件 ID）
make package-idp-plugin name=custom_my_plugin
```

这将生成一个 ConfigMap YAML 文件：

```bash
# 生成的文件名格式：bk-user-idp-plugin-{插件目录名}.yaml
# 例如：custom_my_plugin 会生成 bk-user-idp-plugin-custom-my-plugin.yaml
ls bk-user-idp-plugin-custom-my-plugin.yaml
```

生成的 ConfigMap YAML 内容示例：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bk-user-idp-plugin-custom-my-plugin
data:
  __init__.py: |
    # -*- coding: utf-8 -*-
    from ..base import register_plugin
    from .plugin import CustomMyPlugin

    register_plugin(CustomMyPlugin)

    from ..models import PluginMetadata

    METADATA = PluginMetadata(
        id="custom_my_plugin",
        name="我的自定义插件",
        description="自定义认证插件"
    )

  plugin.py: |
    # -*- coding: utf-8 -*-
    # 插件实现代码...
  ...
```

### 第二步：应用 ConfigMap 到 Kubernetes

将生成的 ConfigMap 应用到 Kubernetes 集群：

```bash
# ${namespace} 表示部署所在命名空间
# 应用 ConfigMap
kubectl apply -n ${namespace} -f bk-user-idp-plugin-custom-my-plugin.yaml

# 验证 ConfigMap 是否创建成功
kubectl get configmap bk-user-idp-plugin-custom-my-plugin -n ${namespace}

# 查看 ConfigMap 详情
kubectl describe configmap bk-user-idp-plugin-custom-my-plugin -n ${namespace}
```

### 第三步：挂载 ConfigMap 到 Pod

修改 `bk-user` 和 `bk-login` 的 helm chart 的 values 配置，将 ConfigMap 挂载到插件目录。

#### bk-user Deployment 配置示例

```yaml
# 调整 bk-user-v3 Release Values，挂载插件
bklogin:
  volumes:
    - name: idp-plugin-custom-my-plugin
      configMap:
        name: bkuser-idp-plugin-custom-my-plugin

  volumeMounts:
    - name: idp-plugin-custom-my-plugin
      mountPath: /app/bklogin/idp_plugins/custom_my_plugin

bkuser:
  volumes:
    - name: idp-plugin-custom-my-plugin
      configMap:
        name: bkuser-idp-plugin-custom-my-plugin

  volumeMounts:
    - name: idp-plugin-custom-my-plugin
      mountPath: /app/bkuser/idp_plugins/custom_my_plugin
```

**⚠️ 重要提示：**
- `mountPath` 必须是 `/app/bkuser/idp_plugins/{插件目录名}` (bk-user) 和 `/app/bklogin/idp_plugins/{插件目录名}` (bk-login)
- 插件目录名必须与打包时的 `name` 参数一致
- bk-user 和 bk-login 都需要挂载插件（因为登录流程在 bk-login 中进行，登录配置在 bk-user 里进行）

### 第四步：通过 Helm 更新 bk-login / bk-user

Deployment 更新后，检查是否正确挂载插件

```bash
# 进入 bklogin-web Deployment 中的一个 pod
kubectl exec -it deployment/bklogin-web -- bash

# 查看目录结构是否符合
/app/bklogin/
├── idp_plugins/                 # 插件包根目录
│   ├── ...
│   │
│   └── custom_xxx/             # 自定义插件
│   │   ├── __init__.py
│   │   ├── plugin.py
│   │   ├── logo.png
│   │   └── ...
│   │
│   ├── ...

# 进入 bkuser-web Deployment 中的一个 pod
kubectl exec -it deployment/bkuser-web -- bash

# 查看目录结构是否符合
/app/bkuser/
├── idp_plugins/                 # 插件包根目录
│   ├── ...
│   │
│   └── custom_xxx/             # 自定义插件
│   │   ├── __init__.py
│   │   ├── plugin.py
│   │   ├── logo.png
│   │   └── ...
│   │
│   ├── ...
```

或者使用 kubectl exec 一键执行：

```bash
# 检查 bk-user 插件目录
kubectl exec deployment/bkuser-web -- ls -la /app/bkuser/idp_plugins/custom_my_plugin

# 检查 bk-login 插件目录
kubectl exec deployment/bklogin-web -- ls -la /app/bklogin/idp_plugins/custom_my_plugin
```

### 第五步：注册插件到数据库

插件加载成功后，需要将插件信息注册到数据库：

```bash
# 进入 bk-user Pod
kubectl exec -it deployment/bkuser-web -- bash

# 在 Pod 中执行注册命令
python manage.py register_idp_plugin --dir_name=custom_my_plugin

# 退出 Pod
exit
```

或者使用 kubectl exec 一键执行：

```bash
kubectl exec deployment/bk-user -- python manage.py register_idp_plugin --dir_name=custom_my_plugin
```

注册成功后会看到提示：

```
register idp plugin [custom_my_plugin] into database successfully.
```

### 更新插件

当插件代码更新时：

```bash
# 1. 重新打包插件
cd src/idp-plugins
make package-idp-plugin name=custom_my_plugin

# 2. 更新 ConfigMap
kubectl apply -n ${namespace} -f bk-user-idp-plugin-custom-my-plugin.yaml

# 3. 重启 deployment 以加载新代码
kubectl rollout restart deployment bkuser-web
kubectl rollout restart deployment bklogin-web
```
