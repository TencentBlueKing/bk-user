FROM python:3.10.12-slim-buster
USER root

RUN rm /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian buster main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian-security buster/updates main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tencent.com/debian buster-updates main" >> /etc/apt/sources.list

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN pip install --upgrade pip setuptools
RUN pip install poetry==1.5.1

WORKDIR /app
COPY src/bk-user/pyproject.toml /app
COPY src/bk-user/poetry.lock /app
RUN poetry config virtualenvs.create false && poetry install --only main

COPY src/bk-user/bkuser /app/bkuser
COPY src/bk-user/bin /app/bin
COPY src/bk-user/manage.py /app

CMD ["bash", "/app/bin/start.sh"]
