#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 自动化同步网关
if [ "$ENABLE_SYNC_APIGW" = true ]; then
  sh ./support-files/bin/sync-apigateway.sh
  sh ./bkuser/apis/open_v3/frontend/support-files/bin/sync-apigateway.sh
fi

# 注册到蓝鲸通知中心
if [ "$ENABLE_BK_NOTICE" = true ]; then
  python manage.py register_application
fi
