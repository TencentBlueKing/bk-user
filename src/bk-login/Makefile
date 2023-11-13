export DJANGO_SETTINGS_MODULE=bklogin.settings

help: ## 展示可用 make 命令及说明
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ 环境初始化

init: ## 初始化 pre-commit, python 依赖包
	pip install pre-commit
	pre-commit install
	pip install poetry==1.5.1
	poetry install


##@ 研发命令

test: ## 执行项目单元测试（pytest）
	pytest --maxfail=1 -l --reuse-db tests --disable-warnings


i18n-po: ## 将源代码 & 模版中的 message 采集到 django.po
	python manage.py makemessages -d django -l en -e html,part -e py
	python manage.py makemessages -d django -l zh_Hans -e html,part -e py

i18n-mo: ## 将 django.po 文件编译成 django.mo 文件
	python manage.py compilemessages

i18n-all: i18n-po i18n-mo  ## 执行 i18n-po & i18n-mo
