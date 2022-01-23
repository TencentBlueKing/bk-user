# 什么是数据源插件

数据源插件，顾名思义，即用于对接不同数据源的插件。用户管理通过插件和各种数据源进行交互，目前包括数据同步、登录两种功能。

# 如何开发一个数据源插件

文件目录树样例
```
src
├── api
│   ├── bkuser_core
│	│	├── categories
│	│	│	└── plugins                  # 插件包存放路径
│	│	│	    ├── custom               # 插件包名
│	│	│	    │	├── __init__.py      # python 包标识文件，注册插件, 必须
│	│	│	    │	├── syncer.py        # 用于数据同步 DB 逻辑处理，必须
│	│	│	    │	├── client.py        # 用于和远端数据交互的客户端封装，示例，非必须
│	│	│	    │	├── login.py         # 用于实现外部登录校验逻辑，需要时必须
│	│	│	    │   ├── metas.py         # 用于定义各种模型在数据同步的基础行为，非必须
│	│	│	    │   └── utils.py         # 用于存放各类工具类、函数，示例，非必须
```

其中 `custom` 即是一个 `插件包`，它同时是一个 `python package`，即必须存在一个 `__init__.py` 文件。


## 注册

所有的插件都是在 API **服务启动**时，以**主动注册**的方式添加。
我们需要在 `__init__.py` 添加注册信息

```python
# -*- coding: utf-8 -*-
from bkuser_core.categories.plugins.plugin import DataSourcePlugin

from .login import LoginHandler
from .syncer import SuperSyncer

# 所有插件都需要初始化一个 DataSourcePlugin 对象
DataSourcePlugin(
    # 插件名，必须全局唯一
    name="superman",
    # Syncer 同步类实现，在 syncer 文件中实现
    syncer_cls=SuperSyncer,
    # 处理登录校验逻辑
    login_handler_cls=LoginHandler,
    # 是否允许通过 client（例如 用户管理 SaaS 更改数据）
    allow_client_write=False,
).register()
```

由于当前版本中，用户目录概念尚未和数据源解耦，我们需要为插件单独创建一个特殊类型——`pluggable`的用户目录
```bash
python manage.py create_pluggable_category --name 插件化目录 --domain some-domain.com --plugin superman
```
默认地，我们会创建一个 key 为 `plugin_name` 的 `Setting` 绑定到该目录。

## 配置

我们为插件增加了申明配置的能力，开发者可以通过 yaml 文件定义面向使用者的配置列表

```python
DataSourcePlugin(
    name="custom",
    syncer_cls=CustomSyncer,
    login_handler_cls=LoginHandler,
    allow_client_write=True,
    category_type="custom",
    hooks={HookType.POST_SYNC: AlertIfFailedHook},
    # 在这里显式地告之插件配置的文件路径
    settings_path=os.path.dirname(__file__) / Path("settings.yaml"),
).register()
```
```yaml
# 默认第一层
settings:
  # namespace
  general:
    # region
    default:
      # 具体配置的 key 值
      paths:
        # SettingMeta 具体内容
        default:
          # 可以以 yaml 原生写法定义 JSON 内容
          profile: "profiles"
          department: "departments"
      api_host:
        default: ""
        example: "https://example.com"
```
当插件加载时，我们会做两件事：
- 创建或更新 SettingMeta
- 当 SettingMeta 的默认值存在时(所有不为 `None` 的内容，空字符串、空字典均被视作 **存在**), 使用默认值为所有已经存在对应目录初始化 Setting

## 同步类 Syncer 实现

在 `src/api/bkuser_core/categories/plugins/base.py` 中，我们实现了一个 `Syncer` 同步器的基类，

原则上我们将给予插件较高的自由度，只需要继承并实现 `sync` 方法即可接入。不过考虑到整体的代码质量和维护性，在内嵌的几个插件中，我们都采用了类似的 `sync` 逻辑实现，可以作为后续开发和评审的参考。 

### DBSyncManager
DB 同步管理器，主要目的是将数据处理操作和 DB 插入（内存操作和 IO 操作）二者分开，提升整体同步速度。支持在将数据模型放入内存对象池，并附带上对应操作（新增 or 更新），然后批量同步到数据库。

具体的使用请参看 `src/api/bkuser_core/categories/plugins/base.py` 中的实现，以及内嵌插件使用样例。

### SyncModelMeta 
   
在 `src/api/bkuser_core/categories/plugins/base.py` 中我们定义了一个 `SyncModelMeta`，作为同步数据模型的元信息描述，通常情况下不需要关心和修改，已经集成在 `DBSyncManager` 中。

如果需要修改可以参考 `custom` 插件中 `metas.py` 的元信息描述。

## 登录 LoginHandler 实现

和 `Syncer` 一样，只需要继承并实现 `src/api/bkuser_core/categories/plugins/base.py` 中 `LoginHandler` 的 `check` 方法即可接入蓝鲸登录。

## 测试插件同步

测试插件同步功能，首先需要确定同步的目录和目录类型，当前目录类型和插件一一对应，需要先确定目录类型和插件的绑定关系，再选择对应的目录进行测试同步。

```bash
# 非 excel 类型，需要预先在 user_settings_setting 表中添加远端数据配置
python manage.py test_category_sync --category_id=2

# 使用本地 excel 类型导入
python manage.py test_category_sync --category_id=1 --excel_file=bkuser_core/tests/categories/plugins/local/assets/fewusers.xlsx
```

# 如何部署一个自定义插件

- 将完整的插件包，放入到 `src/api/bkuser_core/categories/plugins/` 路径下
- 由于所有的插件都是在服务启动时加载，所以任何插件包的增删，都需要重启服务
