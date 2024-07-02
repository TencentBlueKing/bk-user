# 开发指引

## 文件目录释义
```text
bk-user    
├── docs  # 文档
└── src
    ├── bk-login  # 统一登录代码目录
    ├── bk-user   # 用户管理代码目录
    └── pages     # 前端代码
```

## 前置准备
在开始开发前，请确保您使用的 python 版本为 3.10.12（推荐使用 `pyenv` 来管理您本地的 Python 版本）：


``` bash
pyenv install 3.10.12
```

准备 Python 虚拟环境（一项目一环境，互相隔离，推荐 `pyenv` 或者 `poetry` 等虚拟环境管理工具）：

``` bash
virtualenv -p ~/.pyenv/versions/3.10.12/bin/python3 bk-login-venv  
virtualenv -p ~/.pyenv/versions/3.10.12/bin/python3 bk-user-venv
```

此外，您还需要为整个项目安装并初始化 `pre-commit`：

``` bash
pip install pre-commit && pre-commit install
```

目前我们使用了两个工具: `ruff`、`mypy`，它们能保证您的每一次提交都符合预定的开发规范。  
最后进入项目目录，将 `idp_plugin` 软链接到相应的代码目录：

``` bash
ln -s $(pwd)/src/idp-plugins/idp_plugins $(pwd)/src/bk-login/bklogin
ln -s $(pwd)/src/idp-plugins/idp_plugins $(pwd)/src/bk-user/bkuser
```

## 统一登录

### 环境配置
进入 `src/bk-login` 并进入虚拟环境

``` bash
cd src/bk-login
```

安装项目所需的包

``` bash
poetry install
```

在 `bklogin` 目录下添加 `.env` 文件，并在文件里定义以下环境变量

``` bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_NAME=bk_login_db

BK_APP_CODE=bk_login
# 通过蓝鲸开发者中心获取
BK_APP_SECRET="xxx"
# 使用 `from cryptography.fernet import Fernet; Fernet.generate_key()` 生成随机秘钥
BKKRILL_ENCRYPT_SECRET_KEY="xxx"
# 通过蓝鲸开发者中心获取（与用户管理侧配置相同）
BK_USER_APP_SECRET="xxx"
BK_DOMAIN="example.com"
BK_LOGIN_ADDR=login.example.com:8000
```

您可能还需要定义其他的环境变量，详见 `bklogin/settings.py`

### 数据库迁移
``` bash
python manage.py migrate
```

### 启动 Web 服务
``` bash
./bin/start.sh
```

或者

``` bash
python manage.py runserver login.example.com:8000
```

### 检测服务器连通状态
``` bash
curl login.example.com:8000/ping #pong
```

## 用户管理

### 环境配置
进入 `src/bk-login` 并进入虚拟环境
``` bash
cd src/bk-user
```

安装项目所需的包

``` bash
poetry install
```

在 `bklogin` 目录下添加 `.env` 文件，并在文件里定义以下环境变量

``` bash
BK_APP_CODE=bk_user
# 通过蓝鲸开发者中心获取
BK_APP_SECRET="xxx"
# 使用 `from cryptography.fernet import Fernet; Fernet.generate_key()` 生成随机秘钥 
BKKRILL_ENCRYPT_SECRET_KEY="xxx"
BK_DOMAIN="example.com"
BK_USER_URL=http://user.example.com:8000
BK_COMPONENT_API_URL=https://bkapi.example.com
BK_API_URL_TMPL=http://bkapi.example.com/api/{api_name}/

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_NAME=bk_user_db

CELERY_BROKER_URL="" # 该字段为空时则使用 Redis 作为 celery broker
CELERY_WORKER_CONCURRENCY=2

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_MAX_CONNECTIONS=100
REDIS_DB=0

INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=admin_pwd
```

您可能还需要定义其他的环境变量，详见 `bkuser/settings.py`

### 数据库迁移
``` bash
python manage.py migrate
```

### 启动 Web 服务
``` bash
./bin/start.sh
```

或者

``` bash
python manage.py runserver user.example.com:8000
```

### 检测服务器连通状态

``` bash
curl user.example.com:8000/ping #pong
```

### 启动 Celery Worker

``` bash
./bin/start_celery.sh
```

### 启动 Celery Beat
``` bash
./bin/start_celery_beat.sh
```