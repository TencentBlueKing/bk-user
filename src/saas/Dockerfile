FROM node:12.22.12-stretch-slim AS StaticBuilding

ENV NPM_VERSION 6.14.4

# install requirements & build
COPY src/pages /
WORKDIR /
RUN npm i
RUN npm rebuild node-sass --force && npm run build

FROM python:3.6.14-slim-buster as SaaS
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

WORKDIR /app
RUN pip install --upgrade pip setuptools
RUN pip install poetry==1.1.13
RUN poetry config repositories.pypi https://mirrors.tencent.com/pypi/simple/

COPY src/saas/pyproject.toml /app
COPY src/saas/poetry.lock /app
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY src/saas/wsgi.py /app
COPY src/saas/bkuser_shell /app/bkuser_shell
COPY src/saas/locale /app/locale
COPY src/saas/media /app/media
COPY src/saas/manage.py /app
COPY src/saas/RELEASE.yaml /app

COPY src/bkuser_global /app/bkuser_global
COPY --from=StaticBuilding /dist/ /app/static

COPY src/saas/bin/start.sh /app

CMD ["bash", "/app/start.sh"]
