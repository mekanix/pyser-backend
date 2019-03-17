#!/bin/sh


BIN_DIR=`dirname $0`
. ${BIN_DIR}/common.sh
setup

rm -rf pyser/static
flask collect --verbose
rm -rf pyser/static/app
