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

RUN pip install --upgrade pip setuptools
RUN pip install poetry==1.1.13
RUN poetry config repositories.pypi https://mirrors.tencent.com/pypi/simple/

WORKDIR /app
COPY src/api/pyproject.toml /app
COPY src/api/poetry.lock /app
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY src/api/wsgi.py /app
COPY src/api/bkuser_core /app/bkuser_core
COPY src/api/locale /app/locale
COPY src/api/media /app/media
COPY src/api/manage.py /app
COPY src/bkuser_global /app/bkuser_global
COPY src/api/bin/start.sh /app
COPY src/api/bin/start_beat.sh /app
COPY src/api/bin/start_celery.sh /app
COPY src/api/bin/migrate_iam.sh /app
COPY src/api/bin/sync_apigateway.sh /app
COPY src/api/resources /app/resources

CMD ["bash", "/app/start.sh"]
