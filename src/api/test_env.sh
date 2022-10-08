#!/bin/bash

DJANGO_SETTINGS_MODULE="bkuser_core.config.overlays.unittest"
BK_PAAS_URL="http://bkpaas.example.com"
BK_IAM_V3_INNER_HOST="http://bkiam.example.com"
BK_APP_CODE="bk-user"
BK_APP_SECRET="some-default-token"
CELERY_BROKER_URL="redis://:passwordG@localhost:32768/0"
CELERY_RESULT_BACKEND="redis://:passwordG@localhost:32768/0"
