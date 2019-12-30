#!/bin/sh


BIN_DIR=`dirname $0`
FLASK_ENV="production"
NAME=startkit
NUM_WORKERS=4
WSGI_MODULE=wsgi
PORT=${PORT:=9000}
LOG_LEVEL=debug

. ${BIN_DIR}/common.sh
setup
pip install -U gunicorn


exec gunicorn ${WSGI_MODULE}:app \
  --name ${NAME} \
  --workers ${NUM_WORKERS} \
  --bind=:${PORT} \
  --log-level=${LOG_LEVEL} \
  --log-file=- \
  --capture-output
