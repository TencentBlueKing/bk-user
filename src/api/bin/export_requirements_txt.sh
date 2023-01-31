#!/bin/bash

poetry export -f requirements.txt --dev --without-hashes -o requirements.txt --no-ansi

sed -i '/^--extra-index-url*/d' requirements.txt
sed -i '/gevent/d' requirements.txt
sed -i '/greenlet/d' requirements.txt
sed -i '/gunicorn/d' requirements.txt
