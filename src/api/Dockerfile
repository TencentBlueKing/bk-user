FROM mirrors.tencent.com/blueking/python:3.11.13-ts3
USER root

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN dnf install -y gcc gcc-c++ gettext

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf
RUN pip install --upgrade pip setuptools
RUN pip install poetry==1.8.5
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
