FROM node:18.17.1-bullseye-slim AS StaticBuilding
ENV NPM_VERSION 9.6.7

COPY src/bk-login/pages /
WORKDIR /
RUN npm install
RUN npm run build

FROM mirrors.tencent.com/blueking/python:3.11.14-ts4
USER root

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf

RUN dnf install -y mysql-devel gettext
RUN dnf groupinstall -y "Development Tools"

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY src/bk-login/pyproject.toml /app
COPY src/bk-login/uv.lock /app

RUN export UV_PROJECT_ENVIRONMENT=/usr/local/ && uv sync --locked --no-cache

COPY src/bk-login/bklogin /app/bklogin
COPY src/bk-login/bin /app/bin
COPY src/bk-login/manage.py /app
COPY src/idp-plugins/idp_plugins /app/bklogin/idp_plugins
COPY src/bk-login/support-files /app/support-files

COPY --from=StaticBuilding /dist /app/staticfiles
COPY --from=StaticBuilding /dist/index.html /app/templates/index.html

CMD ["bash", "/app/bin/start.sh"]
