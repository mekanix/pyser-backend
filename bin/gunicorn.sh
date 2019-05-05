#!/bin/sh

export LC_LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export PATH="${PATH}:/usr/local/bin"

BIN_DIR=`dirname $0`
FLASK_ENV="production"
NAME=pyser
NUM_WORKERS=4
WSGI_MODULE=wsgi
PORT=${PORT:=9000}
LOG_LEVEL=debug

. ${BIN_DIR}/common.sh
setup


exec gunicorn ${WSGI_MODULE}:app \
  --name ${NAME} \
  --workers ${NUM_WORKERS} \
  --bind=:${PORT} \
  --log-level=${LOG_LEVEL} \
  --log-file=- \
  --capture-output
