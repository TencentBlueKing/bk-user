#!/bin/bash

log_info() {
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${NOW} [INFO] $1"
}

if_error_then_exit() {
    # Usage: if_error_then_exit $? "fail, and exit"
    if [ "$1" -ne 0 ]
    then
        NOW=$(date +"%Y-%m-%d %H:%M:%S")
        echo "${NOW} [ERROR] $2"
        exit 1
    fi
}

echo "====== begin to register apis to apigateway ======"

log_info "do sync_apigw_config..."
python manage.py sync_apigw_config -f /app/resources/apigateway/definition.yaml
if_error_then_exit $? "sync_apigw_config fail"
log_info "done sync_apigw_config"

log_info "do sync_apigw_stage..."
python manage.py sync_apigw_stage -f /app/resources/apigateway/definition.yaml
if_error_then_exit $? "sync_apigw_stage fail"
log_info "done sync_apigw_stage"

log_info "do sync_apigw_resources..."
python manage.py sync_apigw_resources -f /app/resources/apigateway/bk_apigw_resources_bk-user.yaml --delete
if_error_then_exit $? "sync_apigw_resources fail"
log_info "done sync_apigw_resources"

log_info "do sync_resource_docs_by_archive..."
python manage.py sync_resource_docs_by_archive -f /app/resources/apigateway/definition.yaml
if_error_then_exit $? "sync_resource_docs_by_archive fail"
log_info "done sync_resource_docs_by_archive"

log_info "do create_version_and_release_apigw..."
python manage.py create_version_and_release_apigw -f /app/resources/apigateway/definition.yaml --generate-sdks
if_error_then_exit $? "create_version_and_release_apigw fail"
log_info "done create_version_and_release_apigw"


echo "====== sync done. success! ======"
