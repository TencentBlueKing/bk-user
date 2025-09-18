FROM mirrors.tencent.com/blueking/python:3.11.13-ts3
USER root

RUN dnf install -y gcc gcc-c++ gettext

RUN mkdir ~/.pip &&  printf '[global]\nindex-url = https://mirrors.tencent.com/pypi/simple/' > ~/.pip/pip.conf
RUN pip install --upgrade pip setuptools
RUN pip install poetry==1.8.5
RUN poetry config repositories.pypi https://mirrors.tencent.com/pypi/simple/

# for saml 2.0 custom login
RUN dnf install -y libtool-ltdl-devel xmlsec1-devel xmlsec1-openssl-devel
RUN pip install python3-saml==1.16.0 xmlsec==1.3.13

WORKDIR /app
COPY src/login/pyproject.toml /app
COPY src/login/poetry.lock /app
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY src/login/wsgi.py /app
COPY src/login/bklogin /app/bklogin
COPY src/login/locale /app/locale
COPY src/login/static /app/static
COPY src/login/manage.py /app
COPY src/bkuser_global /app/bkuser_global
COPY src/login/bin/start.sh /app

CMD ["bash", "/app/start.sh"]
