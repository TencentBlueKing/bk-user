#!/bin/bash

## 设置环境变量
CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-6}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-info}

command="celery -A bkuser worker -l ${CELERY_LOG_LEVEL} --concurrency ${CELERY_CONCURRENCY}"

## Run!
exec bash -c "$command"
