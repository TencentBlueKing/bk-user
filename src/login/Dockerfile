FROM python:3.6.14-slim-buster
USER root

RUN rm /etc/apt/sources.list && \
    echo "deb https://mirrors.cloud.tencent.com/debian buster main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.cloud.tencent.com/debian buster-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.cloud.tencent.com/debian buster main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.cloud.tencent.com/debian buster-updates main contrib non-free" >> /etc/apt/sources.list

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf

RUN apt-get update && apt-get install -y gcc gettext

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN pip install --upgrade pip
RUN pip install poetry==1.1.7

WORKDIR /app
COPY src/login/pyproject.toml /app
COPY src/login/poetry.lock /app
RUN poetry config experimental.new-installer false && poetry config virtualenvs.create false && poetry install --no-dev

COPY src/login/wsgi.py /app
COPY src/login/bklogin /app/bklogin
COPY src/login/locale /app/locale
COPY src/login/static /app/static
COPY src/login/manage.py /app
COPY src/bkuser_global /app/bkuser_global
COPY src/login/bin/start.sh /app

CMD ["bash", "/app/start.sh"]
