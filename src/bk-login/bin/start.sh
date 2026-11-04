#!/bin/bash

# API 网关到后端使用 HTTP/1.1 长连接（keepalive_timeout 60s），gevent worker 下必须关闭 keep-alive，否则会偶发 502
command="gunicorn bklogin.wsgi -k gevent -w 8 --threads 2 --max-requests 10240 --max-requests-jitter 50 --timeout 60 --keep-alive 0 -b [::]:${PORT:-8000} --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({x-request-id}i)s %(u)s %(t)s \"%(r)s\" %(s)s %(D)s %(b)s \"%(f)s\" \"%(a)s\"'"
exec bash -c "$command"
