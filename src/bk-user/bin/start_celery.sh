#!/bin/bash

# 设置环境变量
CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-8}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-info}

# Run!
celery -A bkuser.celery worker -l ${CELERY_LOG_LEVEL} --concurrency ${CELERY_CONCURRENCY}
