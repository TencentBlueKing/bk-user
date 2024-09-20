#!/bin/bash

command="celery -A bkuser.celery beat -l ${CELERY_LOG_LEVEL:-INFO}"
exec bash -c "$command"
