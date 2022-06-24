#!/usr/bin/env bash

python manage.py collectstatic
python manage.py compilemessages

gunicorn wsgi -w 16 --timeout 150 -b 0.0.0.0:5000 -k gevent --max-requests 1024 --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"' --env prometheus_multiproc_dir=/tmp/
