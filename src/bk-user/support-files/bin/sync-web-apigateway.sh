#!/bin/bash

set -e

gateway_name="bk-user-web"

# 待同步网关、资源定义文件，需调整为实际的配置文件地址
definition_file="support-files/web/definition.yaml"
resources_file="support-files/web/resources.yaml"

echo "gateway sync definition start ..."

# 同步网关基本信息
echo "gateway sync definition start ..."
python manage.py sync_apigw_config --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关环境信息
python manage.py sync_apigw_stage --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关资源
python manage.py sync_apigw_resources --delete --gateway-name=${gateway_name} --file="${resources_file}"

# 同步资源文档
python manage.py sync_resource_docs_by_archive --gateway-name=${gateway_name} --file="${definition_file}"

# 创建资源版本、发布
python manage.py create_version_and_release_apigw --gateway-name=${gateway_name} --file="${definition_file}"

## 为应用主动授权
#python manage.py grant_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"

# 获取网关公钥
python manage.py fetch_apigw_public_key --gateway-name=${gateway_name}

echo "gateway sync definition end"
