#!/usr/bin/env bash

python manage.py collectstatic

command="gunicorn wsgi -w 16 --timeout 150 -b 0.0.0.0:5000 -k gevent --max-requests 1024 --access-logfile '-' --access-logformat '%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" in %(L)s seconds' --log-level INFO --log-file=-"

## Run!
exec bash -c "$command"
