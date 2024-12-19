#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 待同步网关名，需修改为实际网关名；
# - 如在下面指令的参数中，指定了参数 --gateway-name=${gateway_name}，则使用该参数指定的网关名
# - 如在下面指令的参数中，未指定参数 --gateway-name，则使用 Django settings BK_APIGW_NAME
gateway_name="bk-login"

# 待同步网关、资源定义文件，需调整为实际的配置文件地址
definition_file="support-files/definition.yaml"
resources_file="support-files/resources.yaml"

echo "gateway sync definition start ..."

# 同步网关基本信息
echo "gateway sync definition start ..."
python manage.py sync_apigw_config --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关环境信息
python manage.py sync_apigw_stage --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关资源
#
# --delete: 当资源在服务端存在，却未出现在资源定义文件中时，指定本参数会强制删除这类资源，以保证服务端资源和文件内容完全一致。
#           如果未指定本参数，将忽略未出现的资源
# --doc_language: en/zh  是否生成接口文档(中文/英文)
python manage.py sync_apigw_resources --delete --gateway-name=${gateway_name} --file="${resources_file}"

# 可选，同步资源文档
python manage.py sync_resource_docs_by_archive --gateway-name=${gateway_name} --file="${definition_file}"

# 创建资源版本、发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK  指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
python manage.py create_version_and_release_apigw --gateway-name=${gateway_name} --file="${definition_file}"

# 可选，为应用主动授权
python manage.py grant_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"

# 获取网关公钥
python manage.py fetch_apigw_public_key --gateway-name=${gateway_name}

echo "gateway sync definition end"
