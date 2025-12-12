FROM node:18.17.1-bullseye-slim AS StaticBuilding
ENV NPM_VERSION 9.6.7

COPY src/pages /
WORKDIR /
RUN npm install --legacy-peer-deps
RUN npm run build

FROM mirrors.tencent.com/blueking/python:3.11.14-ts4
USER root

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf

RUN dnf install -y mysql-devel gettext && \
    dnf groupinstall -y "Development Tools"

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ARG BK_BUILD_VERSION="tag: null, commitID: ^HEAD, buildID: null, buildTime: null"
ENV BK_BUILD_VERSION=${BK_BUILD_VERSION}

COPY src/bk-user/pyproject.toml /app
COPY src/bk-user/uv.lock /app

RUN export UV_PROJECT_ENVIRONMENT=/usr/local/ && uv sync --locked --no-cache

COPY src/bk-user/bkuser /app/bkuser
COPY src/bk-user/bin /app/bin
COPY src/bk-user/media /app/media
COPY src/bk-user/version_log /app/version_log
COPY src/bk-user/locale /app/locale
COPY src/bk-user/manage.py /app
COPY src/idp-plugins/idp_plugins /app/bkuser/idp_plugins
COPY src/bk-user/support-files /app/support-files

COPY --from=StaticBuilding /dist /app/staticfiles
COPY --from=StaticBuilding /dist/index.html /app/templates/index.html

CMD ["bash", "/app/bin/start.sh"]
