# 数据源插件开发指南

## 目录 & 文件说明

以 LDAP 为例，需要在 `bkuser/plugins` 下新建 ldap 文件夹，目录示例如下：

```
ldap
├── __init__.py
├── exceptions.py
├── models.py
└── plugin.py
```

### exceptions.py

`exceptions.py`
存储该插件可能抛出的各类异常，需要注意的是，所有异常必须继承自 `bkuser.plugins.exceptions.BaseDataSourcePluginError`
，更推荐的做法是每种插件拥有自己的 `BaseException`，具体示例如下：

```python
from bkuser.plugins.exceptions import BaseDataSourcePluginError


class LDAPDataSourcePluginError(BaseDataSourcePluginError):
    """LDAP 数据源插件基础异常"""


class XXXError(LDAPDataSourcePluginError):
    """LDAP xxx 异常"""
```

### models.py

`models.py` 存储该插件的配置类建模，我们采用 pydantic(v2)
来对配置类进行建模，所有的配置类模型都需要继承自 `pydantic.BaseModel`，且需要通过 `model_validator` 等方式，支持使用该模型对用户的输入进行校验。

建模示例可参考 [models.py](./local/models.py)

### plugin.py

`plugin.py` 是插件的入口，所有插件类需要继承自 `bkuser.plugins.base.BaseDataSourcePlugin` 并实现对应的方法。

插件设计示例及说明如下：

```python
from bkuser.plugins.base import BaseDataSourcePlugin

class LDAPDataSourcePlugin(BaseDataSourcePlugin):
    """LDAP 数据源插件"""

    config_class = LDAPDataSourcePluginConfig

    def __init__(self, plugin_config: LDAPDataSourcePluginConfig):
        self.plugin_config = plugin_config

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        ...

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        ...

    def test_connection(self) -> TestConnectionResult:
        """测试连通性"""
        ...
```

### \_\_init\_\_.py

在插件编写完成后，还需要在 `__init__.py` 中调用 register_plugin 以注册插件，示例如下：

```python
from bkuser.plugins.base import register_plugin
from bkuser.plugins.constants import DataSourcePluginEnum

from .plugin import LDAPDataSourcePlugin

register_plugin(DataSourcePluginEnum.LDAP, LDAPDataSourcePlugin)
```

## 注意事项

TODO 待补充
