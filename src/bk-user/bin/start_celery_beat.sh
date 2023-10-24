#!/bin/bash

# 设置环境变量
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-info}

# Run!
celery -A bkuser.celery beat -l ${CELERY_LOG_LEVEL} --scheduler django_celery_beat.schedulers:DatabaseScheduler
