#! /bin/bash

# 激活虚拟环境
poetry shell

python manage.py migrate || true
python manage.py runserver 0.0.0.0:8004
