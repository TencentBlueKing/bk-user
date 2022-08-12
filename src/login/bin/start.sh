#!/usr/bin/env bash

python manage.py collectstatic
python manage.py compilemessages


command="gunicorn wsgi -w 16 --timeout 150 -b [::]:5000 -k gevent --max-requests 1024 --access-logfile '-' --access-logformat '%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" in %(L)s seconds' --log-level INFO --log-file=- --env prometheus_multiproc_dir=/tmp/"

## Run!
exec bash -c "$command"