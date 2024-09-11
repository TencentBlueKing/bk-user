#!/bin/bash

python manage.py compilemessages

command="gunicorn bkuser.wsgi -k gevent -w 8 --threads 2 --max-requests 10240 --max-requests-jitter 50 --timeout 60 -b [::]:${PORT:-8001} --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s \"%(r)s\" %(s)s %(D)s %(b)s \"%(f)s\" \"%(a)s\"'"
exec bash -c "$command"
