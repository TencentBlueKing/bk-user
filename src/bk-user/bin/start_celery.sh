#!/bin/bash

command="celery -A bkuser.celery worker -l ${CELERY_LOG_LEVEL:-INFO} --concurrency ${CELERY_WORKER_CONCURRENCY:-8}"
exec bash -c "$command"
