#!/bin/bash

python manage.py collectstatic --no-input

LISTEN_PORT="${PORT:=8000}"
gunicorn bkuser.wsgi -w 8 --threads 2 --max-requests 1024 --max-requests-jitter 50 --worker-class gevent -b [::]:$LISTEN_PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
