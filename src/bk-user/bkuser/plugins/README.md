# 自定义数据源插件开发指南

## 目录 & 文件说明

假设你要开发名为 Fox 的数据源插件，则需要在 `bkuser/plugins` 下新建 fox 文件夹，目录示例如下：

```
fox
├── __init__.py
├── exceptions.py
├── logo.png
├── models.py
└── plugin.py
```

### exceptions.py

`exceptions.py`
存储该插件可能抛出的各类异常，需要注意的是，所有异常必须继承自 `bkuser.plugins.exceptions.BaseDataSourcePluginError`
，更推荐的做法是每种插件拥有自己的 `BaseException`，具体示例如下：

```python
from bkuser.plugins.exceptions import BaseDataSourcePluginError


class FoxDataSourcePluginError(BaseDataSourcePluginError):
    """Fox 数据源插件基础异常"""


class XXXError(FoxDataSourcePluginError):
    """Fox 数据源插件 xxx 异常"""
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


class FoxDataSourcePlugin(BaseDataSourcePlugin):
    """Fox 数据源插件"""

    # 注：非内置插件请使用字符串作为 ID，且需要以 `custom_` 为前缀
    id = "custom_fox"
    # 插件配置类建模
    config_class = FoxDataSourcePluginConfig

    def __init__(self, plugin_config: FoxDataSourcePluginConfig):
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

from .plugin import FoxDataSourcePlugin

register_plugin(FoxDataSourcePlugin)

# 注意：如果这是一个自定义插件（非蓝鲸官方内置），还需要设置插件 Metadata 信息
from bkuser.plugins.models import PluginMetadata

METADATA = PluginMetadata(
    # 插件唯一 ID
    id=FoxDataSourcePlugin.id,
    # 插件展示用名称
    name="FoxIsNotDonkey",
    # 插件展示用描述
    description="The fox is a nimble, smart creature known for its unique red-brown fur and bushy tail."
)
```

### logo.png

数据源插件 Logo，仅支持 PNG 格式（推荐尺寸 1024 * 1024）；如果未提供则会使用默认 Logo。

## 注意事项

在将数据源插件实现的源代码目录挂载到 `bkuser/plugins` 目录下后，还需要在服务运行起来后，执行以下命令以在 DB 中添加插件信息：

```shell
python manage.py register_data_source_plugin --dir_name=fox
```
