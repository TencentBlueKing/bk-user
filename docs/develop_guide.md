# 开发指引

## 文件目录释义
```text
├── docs  # 文档
├── deploy  # 部署工具
└── src
    ├── api  # 后台 API 代码目录
    ├── bkuser_global  # 公共代码目录
    ├── pages  # SaaS 前端代码
    ├── login  # 蓝鲸登录代码（包含前端 + 后台）
    ├── sdk  # 由 API 生成的 SDK 代码
    └── saas  # SaaS 后端代码
```

本地开发时，你需要分别为四个模块——后台 API、SaaS 前端、SaaS 后端、蓝鲸登录——创建开发环境。

在开始开发前，你需要为整个项目安装并初始化 `pre-commit`，

``` bash
pre-commit install
```

目前我们使用了四个工具: `isort`、`black`、`flake8`、`mypy`，它们能保证你的每一次提交都符合我们预定的开发规范。


## API 开发

API 是我们整个产品的核心项目，它的开发环境会稍微复杂一些，你可以查阅 [蓝鲸用户管理核心 API 开发指引](develop_api_guide.md) 了解更多。

## SaaS 后端开发

和 API 开发类似，你需要首先链接公共代码（API 如果做过就可以跳过了）

```bash
make link
```

然后需要安装依赖

```bash
cd src/saas/
poetry install
```

依旧和 API 类似，你需要创建本地开发配置，可以完全参照上一个项目操作。

运行
```bash
bash bin/start_dev.sh
```

## SaaS 前端开发

### 安装依赖
```bash
cd src/pages
npm install
```

### 修改测试 html

你可以修改 `index-dev.html` 中的具体变量，来指向你自己的开发环境。

### 运行
```bash
npm run dev
```

## 蓝鲸登录开发
与 SaaS 类似，你需要首先链接公共代码（前面任意一步做过即可跳过）
```bash
make link
```

### 安装依赖
```bash
cd src/login
poetry install
```

运行
```bash
bash bin/start_dev.sh
```
